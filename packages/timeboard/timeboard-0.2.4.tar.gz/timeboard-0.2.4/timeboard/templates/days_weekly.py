from __future__ import division
from timeboard.core import get_timestamp, Organizer
from timeboard.utils import is_string, to_iterable, assert_value
from timeboard.templates.base import TemplateMixin, TimeboardFactory, FilterCondition
import timeboard.when as when

from pandas import period_range, Period
import datetime
import warnings


class DaysWeeklyTemplateSchemeMixin(TemplateMixin):

    @staticmethod
    def assert_weekend(weekend):
        if len(weekend) > 5:
            return False
        if len(weekend) == 1 and not 0 <= weekend[0] <= 6:
            return False
        for i in range(len(weekend) - 1):
            if weekend[i] == 6 and weekend[i + 1] != 0:
                return False
            if weekend[i] < 6 and weekend[i + 1] != weekend[i] + 1:
                return False
            if weekend[i] > 6:
                return False
        return True

    _scheme = dict(

            defaults=dict(      # Timeboard params that we do NOT accept from a caller
                base_unit_freq = 'D',           # fixed value for this template
                layout = None,                  # must be defined in config
                worktime_source = 'duration',   # fixed value for this template
                amendments=None,                # must be defined in config
            ),

            general=dict(       # scheme for all elements of config except config['amend']
                # key = (required=True or False, value_render_function, value_test_function, default_value or None)
                template = (True, str, lambda x: x=='days_weekly', None),
                description = (False, str, None, "Weekly calendar"),
                weekday_labels = (True, to_iterable, lambda x: len(x) == 7, None),
                start = (True, get_timestamp, None, None),
                end = (True, get_timestamp, None, None),
                holiday_label = (False, None, None, 0),
                weekend = (False, to_iterable, assert_weekend.__func__, [5, 6]),
                long_weekends = (False, str, lambda x: x in ['none', 'previous',
                                                             'next', 'nearest'], 'none'),
            ),

            amend=dict(             # scheme for an element of config['amend'] list
                name = (True, str, None, None),
                label = (False, None, None, '$holiday_label'),
                long_weekends = (False, None, None, '$long_weekends'),
                observance = (True, str, lambda x: x in ['day_of_month',
                                                         'nth_weekeday_of_month',
                                                         'from_easter_western',
                                                         'from_easter_orthodox',
                                                         'date'], None),
                when = (True, dict, lambda x: len(x) > 0, None)
            )
        )

    @classmethod
    def _validate(cls, config):

        def validate_parameter(parameter, config, specification):
            required, render_func, test_func, default_v = specification
            try:
                value = config[parameter]
            except KeyError:
                if required:
                    raise KeyError("Required config param '{}' is missing".format(parameter))
                else:
                    value = default_v
            return assert_value(value, render_func, test_func, title=parameter)

        amend = config.pop('amend', [])
        for param, specification in cls._scheme['general'].items():
            value = validate_parameter(param, config, specification)
            config[param] = value
        for amend_spec in amend:
            for param, specification in cls._scheme['amend'].items():
                value = validate_parameter(param, amend_spec, specification)
                if is_string(value) and value.startswith('$'):
                    value = config[value[1:]]
                amend_spec[param] = value

        config['amend'] = amend
        return config


    @classmethod
    def _compile(cls, config, custom_parameters):
        # in custom_parameters we are concerned about 'start', 'end', and 'weekday_labels'

        tb_params = dict()
        given_params = custom_parameters.copy()

        # override certain tb params with predefined settings for this template
        overriden = []
        for param, value in cls._scheme['defaults'].items():
            tb_params[param] = value
            if given_params.pop(param, None) is not None:
                overriden.append(param)
        if overriden:
            warnings.warn("These timeboard parameters will be overriden by template: ".
                          format(overriden), SyntaxWarning)

        updated_cofig = cls.set_custom_bounds(config, given_params)
        tb_params['start'], tb_params['end'] = updated_cofig['start'], updated_cofig['end']
        _ = given_params.pop('start', None)
        _ = given_params.pop('end', None)

        weekday_labels = given_params.pop('weekday_labels', config['weekday_labels'])
        if len(weekday_labels) != 7:
            raise ValueError("`weekday_labels` must be of length 7. Got {}".
                             format(weekday_labels))
        tb_params['layout'] = Organizer('W', structure=[weekday_labels])

        # everything else in `given_params` is assumed to be other Timeboard() kwargs
        # - that is those being not controlled by the template
        tb_params.update(given_params)

        return tb_params, dict(), updated_cofig

    @staticmethod
    def _when_wrapper(when_func):

        def _amendment_calculator(label, start, end, when):
            # when is dict from config['amend'][n]['when']
            pi = period_range(start=start, end=end, freq='A')
            dates = when_func(pi, **when)
            return {date: label
                    for date in dates[(dates >= start) & (dates <= end)]}

        return _amendment_calculator

    @staticmethod
    def _fixed_date_amender(label, start, end, when):
        # when is dict from config['amend'][n]['when']
        dates = when['dates']
        return {date: label
                for date in [Period(d, freq='D').to_timestamp(how='s')
                             for d in dates]
                if start <= date <= end}

    @staticmethod
    def _extend_weekends(amendments, settings, weekend):
        """Make a weekday a day off if a holiday falls on the weekend.

        This function is to be used to update a (part of) `amendments` dictionary
        for a day-based calendar.

        Parameters
        ----------
        amendments: dict
        settings : dict
            Keys are the same as in `amendments`. Values are one of {'none', 'previous',
            'next', 'nearest'}.
            Which weekday to make a day off: a weekday preceding the weekend,
            a weekday following the weekend, or a weekday nearest to the holiday.
            If there is a tie with 'nearest', it works the same way as 'next'.
        weekend: list, optional
            Weekdays constituting weekend, Monday is 0, Sunday is 6. Days must be
            consecutive: i.e. if weekend is on Sunday and Monday, weekend=[6,0],
            NOT weekend=[0,6]. By default weekend is Saturday and Sunday.

        Returns
        -------
        dict
            Updated `amendments` dictionary with new days off, if any. The keys
            are timestamps (both for the old and the new elements.) The values
            of the newly added days are set to the value of `label` if given;
            otherwise, the label of the corresponding holiday is used.

        Notes
        -----
        If a weekday has been already declared a day off because of another holiday
        taking place on the same weekend or it is a holiday by itself, the next
        weekday in the direction specified by `how` parameter will be made
        a day off.
        """
        for holiday in sorted(amendments.keys()):
            how = settings[holiday]
            if how == 'none':
                continue
            day_of_week = holiday.weekday()
            try:
                loc_in_wend = weekend.index(day_of_week)
            except ValueError:
                continue
            _label = amendments[holiday]
            if how == 'previous':
                first_step = -(loc_in_wend + 1)
                step = -1
            elif how == 'next':
                first_step = len(weekend) - loc_in_wend
                step = 1
            elif how == 'nearest':
                if loc_in_wend < len(weekend) // 2:
                    first_step = -(loc_in_wend + 1)
                    step = -1
                else:
                    first_step = len(weekend) - loc_in_wend
                    step = 1
            else: # unrecognized type of long_weekends
                continue
            new_day = holiday + datetime.timedelta(days=first_step)
            while new_day in amendments:
                new_day += datetime.timedelta(days=step)
            amendments[new_day] = _label

        return amendments

    @classmethod
    def _amend(cls, config):
        amenders = dict(
            day_of_month=cls._when_wrapper(when.from_start_of_each),
            nth_weekeday_of_month=cls._when_wrapper(when.nth_weekday_of_month),
            from_easter_western=cls._when_wrapper(when.from_easter_western),
            from_easter_orthodox=cls._when_wrapper(when.from_easter_orthodox),
            date=cls._fixed_date_amender,
        )

        amendments = dict()
        long_weekend_settings = dict()
        for amend_spec in config['amend']:
            amender = amenders[amend_spec['observance']]
            label = amend_spec.get('label') #, config['holiday_label'])
            long_weekends = amend_spec.get('long_weekends') #, config['long_weekends'])
            new_amendments = {get_timestamp(k): v for k, v in
                amender(label, config['start'], config['end'], amend_spec['when']).items()}
            amendments.update(new_amendments)
            long_weekend_settings.update({key: long_weekends for key in new_amendments.keys()})

        amendments = cls._extend_weekends(amendments, long_weekend_settings, config['weekend'])
        return amendments


class BusinessCalendarFactory(DaysWeeklyTemplateSchemeMixin, TimeboardFactory):
    pass

    def _compile(self, *args, **kwargs):

        for deprec, actual in [('custom_start', 'start'), ('custom_end', 'end')]:
            if deprec in kwargs:
                warnings.warn(
                    "{} parameter is deprecated, use {} instead".format(deprec, actual),
                    DeprecationWarning
                )
                if actual in kwargs:
                    raise ValueError("{} and {} are mutually exclusive calendar parameters "
                                     "but both wer given".format(deprec, actual))
                kwargs[actual] = kwargs.pop(deprec)

        return TimeboardFactory._compile(*args, **kwargs)

    def parameters(self):
        warnings.warn(
            "`parameters()` call on a calendar factory is deprecated, "
            "use `make_parameters(**custom_parameters)` insead",
            DeprecationWarning
        )
        tb_parameters = self.make_parameters()
        return {
            'base_unit_freq': tb_parameters['base_unit_freq'],
            'start': get_timestamp(tb_parameters['start']),
            'end': get_timestamp(tb_parameters['end']),
            'layout': tb_parameters['layout'],
            'worktime_source': tb_parameters['worktime_source'],
        }

    def amendments(self, *args, **kwargs):
        warnings.warn(
            "`amendments()` call on a calendar factory is deprecated, "
            "use `make_parameters(**custom_parameters)` insead",
            DeprecationWarning
        )
        tb_parameters = self.make_parameters(*args, **kwargs)
        return tb_parameters['amendments']

    # def _parse_scope_kwargs(self, kwargs):
    #     scope_filter = dict()
    #     remaining_kwargs = kwargs
    #     return scope_filter, remaining_kwargs
    #
    # def _parse_amendment_specific_kwargs(self, config, kwargs):
    #     amendment_filter = dict()
    #     do_not_observe = kwargs.pop('do_not_observe', [])
    #     if do_not_observe:
    #         amendment_filter['name'] = FilterCondition(name='name',
    #                                                    values=_to_iterable(do_not_observe),
    #                                                    include=False,
    #                                                    required=False)
    #     scope_filter, remaining_kwargs = self._parse_scope_kwargs(kwargs)
    #     amendment_filter.update(scope_filter)
    #     return amendment_filter, remaining_kwargs, config