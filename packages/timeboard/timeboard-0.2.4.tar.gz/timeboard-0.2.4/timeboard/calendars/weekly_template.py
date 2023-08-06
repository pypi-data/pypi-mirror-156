from __future__ import division
from ..exceptions import OutOfBoundsError
from ..core import get_timestamp, get_period, is_iterable, to_iterable
from ..timeboard import Timeboard, Organizer
from pandas import period_range, Period
import numpy as np
import yaml
from ..when import (from_start_of_each,
                   nth_weekday_of_month,
                   from_easter_western, from_easter_orthodox)
import datetime
import warnings


def _search_array(a, v):
    """Search sorted array a for values in array v
    Return (v_in_a: array, v_not_in_a: array)
    """
    selector1 = v <= a[-1]
    v1 = v[selector1]
    v2 = v[~selector1]
    selector2 = a[np.searchsorted(a, v1)] == v1
    v_in_a = v1[selector2]
    v_not_in_a = np.concatenate((v1[~selector2], v2))
    return v_in_a, v_not_in_a


def extend_weekends(new_amendments, amendments,
                    how='nearest', label=None, weekend=None):
    assert how in ['previous', 'next', 'nearest']
    if weekend is None:
        weekend = [5, 6]  # Saturday and Sunday
    new_amendments = {get_timestamp(k): v for k, v in new_amendments.items()}
    amendments = {get_timestamp(k): v for k, v in amendments.items()}
    result = dict()
    for holiday in sorted(new_amendments.keys()):
        day_of_week = holiday.weekday()
        try:
            loc_in_wend = weekend.index(day_of_week)
        except ValueError:
            if holiday not in amendments:
                result[holiday] = new_amendments[holiday]
                continue
        if label is None:
            _label = new_amendments[holiday]
        else:
            _label = label
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
        new_day = holiday + datetime.timedelta(days=first_step)
        while new_day in amendments:
            new_day += datetime.timedelta(days=step)
        result[new_day] = _label

    return result


def _when_wrapper(when_func):

    def _amendment_calculator(label, start, end, **kwargs):
        pi = period_range(start=start, end=end, freq='A')
        when_func_kwargs=kwargs['when']
        dates = when_func(pi, **when_func_kwargs)
        return {date: label
                for date in dates[(dates >= start) & (dates <= end)]}

    return _amendment_calculator


def _fixed_date_amender(label, start, end, when):
    dates = when['dates']
    return {date: label
            for date in [Period(d, freq='A').to_timestamp(how='s')
                         for d in dates]
            if date >= start and date <= end}


def read_config(filename):
    with open(str(filename), 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    if config is None:
        return dict()
    return config


class WeeklyTemplate(object):

    def __init__(self, config_dict, custom_amenders=None):
        self._config = self._check_and_normalize_config(config_dict)
        self._parameters=dict(
            base_unit_freq='D',
            start=self._config['start'],
            end=self._config['end'],
            layout=Organizer(marker='W', structure=[self._config['weekday_labels']]),
            worktime_source='labels',
            amendments=None,
        )
        self._amenders=dict(
            day_of_month=_when_wrapper(from_start_of_each),
            nth_weekeday_of_month=_when_wrapper(nth_weekday_of_month),
            from_easter_western=_when_wrapper(from_easter_western),
            from_easter_orthodox=_when_wrapper(from_easter_orthodox),
            date=_fixed_date_amender,
        )


    def _check_and_normalize_config(self, config_dict):

        def check_keys(d, required_keys, optional_keys,
                       context="calendar _config"):
            try:
                key_gen = d.keys()
            except AttributeError:
                raise TypeError("{} must be dict-like".format(context))
            for key in key_gen:
                try:
                    required_keys[key] -= 1
                except KeyError:
                    try:
                        _ = optional_keys[key]
                    except KeyError:
                        raise ValueError(
                            "Unrecognized {} parameter '{}'".
                            format(context, key))
            if sum(required_keys.values()) != 0:
                missing = ", ".join(
                    [k for k, v in required_keys.items() if v !=0 ])
                raise ValueError("Following required parameters are missing "
                                 "from {}: {}".format(context, missing))
            return True

        def check_and_normalize_values(d):
            long_weekends_values = ['none', 'previous', 'next', 'nearest']

            if 'start' in d:
                d['start'] = get_timestamp(str(d['start']))
            if 'end' in d:
                d['end'] = get_timestamp(str(d['end']))
            if ('long_weekends' in d and
                    d['long_weekends'] not in long_weekends_values):
                raise ValueError(
                    "Unrecognized value of 'long_weekends' parameter: "
                    "{}".format(d['long_weekends']))
            for param in ['scopes', 'when']:
                if param in d:
                    try:
                        l = len(list(d[param].keys()))
                    except AttributeError:
                        raise TypeError("Parameter '{}' must be dict-like".
                                        format(param))
                    if l==0:
                        raise ValueError("No value received for parameter '{}'".
                                         format(param))
            return True

        required_keys = dict(
                             weekday_labels=1,
                             holiday_label=1,
                             start=1,
                             end=1)
        optional_keys = dict(
            template="",
            description="(no description provided)",
            long_weekends="none",
            scopes=dict(),
            amend=[])

        check_keys(config_dict, required_keys, optional_keys)
        checked_config_dict = config_dict.copy()
        if (not is_iterable(checked_config_dict['weekday_labels'])
            or len(checked_config_dict['weekday_labels']) != 7):
            raise ValueError("Parameter weekday_labels: expected  "
                             "an iterable of length 7; received {!r}".
                             format(checked_config_dict['weekday_labels']))
        check_and_normalize_values(checked_config_dict)

        checked_config_dict['names'] = set()
        if 'amend' in checked_config_dict:
            for item in checked_config_dict['amend']:
                item_required_keys = dict(
                    observance=1,
                    when=1
                )
                item_optional_keys = dict(
                     template=1,
                     name=1,
                     long_weekends=1,
                     label=1,
                     start=1,
                     end=1,
                     scopes=1
                )
                check_keys(item, item_required_keys, item_optional_keys,
                           context='amend item')
                check_and_normalize_values(item)
                if 'name' in item:
                    checked_config_dict['names'].add(item['name'])

        for param, default_value in optional_keys.items():
            if param not in checked_config_dict:
                checked_config_dict[param] = default_value

        return checked_config_dict

    @property
    def pattern(self):
        return self._config['weekday_labels']

    @property
    def start(self):
        return self._config['start']

    @property
    def end(self):
        return self._config['end']

    @property
    def names(self):
        return self._config['names']

    @property
    def scopes(self):
        return self._config['scopes']

    def parameters(self):
        return self._parameters

    # for API backwatd compatibility only
    def amendments(self):
        return self._parameters['amendments']

    def __repr__(self):
        return "WeeklyTemplate '{}'".format(self._config['description'])

    def __call__(self, *args, **kwargs):
        self.process(*args, **kwargs)
        return self.make_calendar()

    def _extend_duplicate_holidays(self, amnd_item):

        def step_generator(rule):

            generator_config = {
                'previous': [-1],                 # out: -1, -2, -3, -4, -5, -6
                'next': [1],                      # out: 1, 2, 3, 4, 5, 6
                'nearest': [-1, 1],               # out: -1, 1, -2, 2, -3, 3
                'nearest-past-first': [-1, 1],    # same as 'nearest'
                'nearest-future-first': [1, -1],  # out: 1, -1, 2, -2, 3, -3
            }

            assert rule in generator_config.keys()

            multiplier = 1
            while True:
                for basic_step in generator_config[rule]:
                    yield basic_step * multiplier
                multiplier += 1



    def _check_time(self, t):
        if not self._config['start'] <= t <= self._config['end']:
            raise OutOfBoundsError("Point in time '{}' is outside {}"
                                   .format(t, self))

    def _get_bounds(self, custom_start=None, custom_end=None):
        if custom_start is None:
            start = get_timestamp(self._config['start'])
        else:
            start = get_timestamp(custom_start)
            self._check_time(start)
        if custom_end is None:
            end = get_timestamp(self._config['end'])
        else:
            end = get_timestamp(custom_end)
            self._check_time(end)
        return start, end

    def _compute_amendments_from_config(self, do_not_observe, **scope_kwargs):

        arg_scopes = set(scope_kwargs.keys())
        amendments = dict()

        def skip_this_item(item):
            if 'name' in item and item['name'] in do_not_observe:
                return True
            item_scopes = set(
                item['scopes'].keys()) if 'scopes' in item else set()
            for scope in item_scopes.intersection(arg_scopes):
                if not set(to_iterable(scope_kwargs[scope])).issubset(
                        set(to_iterable(item['scopes'][scope]))):
                    return True

            return False

        for item in [i for i in self._config['amend'] if not skip_this_item(i)]:

            if 'start' in item and item['start'] > self._config['start']:
                start = item['start']
            else:
                start = self._config['start']
            if 'end' in item and item['end'] > self._config['end']:
                end = item['end']
            else:
                end = self._config['end']
            long_weekends = item['long_weekends'] if 'long_weekends' in item \
                else self._config['long_weekends']
            label = item['label'] if 'label' in item \
                else self._config['holiday_label']
            if start < self._parameters['start']:
                start = self._parameters['start']
            if end > self._parameters['end']:
                end = self._parameters['end']
            amender_kwargs = {'when': item['when']}
            item_amendments = self._amenders[item['observance']](
                label, start, end, **amender_kwargs)
            if long_weekends != 'none':
                item_amendments = extend_weekends(
                    item_amendments, amendments, how=long_weekends)
            amendments.update(item_amendments)

        return amendments

    def process(self, custom_start=None, custom_end=None, do_not_amend=False,
                       only_custom_amendments=False, custom_amendments=None,
                       do_not_observe=None, **scope_kwargs):

        self._parameters['start'], self._parameters['end'] = self._get_bounds(
            custom_start, custom_end)

        if do_not_observe is None:
            do_not_observe = []

        self._parameters['amendments'] = dict()

        #`do_not_amend` parameter must be deprecated
        if do_not_amend:
            return

        if not only_custom_amendments:
            self._parameters['amendments'].update(
                self._compute_amendments_from_config(do_not_observe,
                                                     **scope_kwargs)
            )

        if custom_amendments is not None:
            freq = self._parameters['base_unit_freq']
            self._parameters['amendments'].update(
                {get_period(k, freq=freq).start_time: v
                 for k, v in custom_amendments.items()}
            )

    def make_calendar(self):
        if self._parameters['amendments'] is None:
            raise RuntimeError("{cls}.process() must be called prior to "
                               "{cls}.make_calendar()".format(cls=self.__class__))
        return Timeboard(**self._parameters)

#------------------------------------

def assert_value(x, value_render_function, value_test_function, title='Parameter'):
    if value_render_function is not None:
        x = value_render_function(x)
    if value_test_function is not None:
        assert value_test_function(x), "Got invalid {} = {!r}".format(title, x)
    return x


days_weekly_config_scheme=dict(

    general=dict(
        # key = (required=True or False, value_render_function, value_test_function, default_value or None)
        template = (True, str, lambda x: x=='days_weekly', None),
        description = (False, str, None, "Weekly calendar"),
        weekday_labels = (True, list, lambda x: len(x)==7, None),
        start = (True, get_timestamp, None, None),
        end = (True, get_timestamp, None, None),
        holiday_label = (False, None, None, 0),
        long_weekends = (False, str, lambda x: x in ['none', 'previous',
                                                     'next', 'nearest'], 'none'),
    ),
    amend=dict(
        name = (True, str, None, None),
        label = (False, None, None, None),
        observance = (True, str, lambda x: x in ['day_of_month',
                                                 'nth_weekeday_of_month',
                                                 'from_easter_western',
                                                 'from_easter_orthodox',
                                                 'date'], None),
        when = (True, dict, lambda x: len(x) > 0, None)
    )
)



def set_custom_bounds(template_config, custom_params):
    custom_start = template_config['start']
    custom_end = template_config['end']
    if 'start' in custom_params:
        if not template_config['start'] <= custom_params['start'] <= template_config['end']:
            raise OutOfBoundsError("Point in time '{}' is outside the range [{}, {}] "
                "of template {}".format(custom_params['start'], template_config['start'],
                                        template_config['end'], template_config['template']))
        custom_start = custom_params['start']
    if 'end' in custom_params:
        if not custom_start <= custom_params['end'] <= template_config['end']:
            raise OutOfBoundsError("Point in time '{}' is outside the range [{}, {}] "
                "of template {}".format(custom_params['start'], custom_start,
                                        template_config['end'], template_config['template']))
        custom_end = custom_params['end']
    return custom_start, custom_end

def days_weekly_compiler(config, custom_parameters):
    tb_params = custom_parameters.copy()
    # override ceratain tb params with predefined settings for this template
    overriden = [kw for kw in ['base_unit_freq', 'layout', 'worktime_source']
                 if kw in custom_parameters]
    if overriden:
        warnings.warn("These timeboard parameters will be overriden by template: ".
                      format(overriden), SyntaxWarning)
    tb_params['base_unit_freq'] = 'D'
    tb_params['layout'] = Organizer(marker='W', structure=[config['weekday_labels']]),
    tb_params['worktime_source'] = 'labels'
    tb_params['start'], tb_params['end'] = set_custom_bounds(config, custom_parameters)

    return tb_params

def days_weekly_amender(config):

    amenders = dict(
        day_of_month=_when_wrapper(from_start_of_each),
        nth_weekeday_of_month=_when_wrapper(nth_weekday_of_month),
        from_easter_western=_when_wrapper(from_easter_western),
        from_easter_orthodox=_when_wrapper(from_easter_orthodox),
        date=_fixed_date_amender,
    )

    amendments = dict()
    for amend_spec in config['amend']:
        if 'label' not in amend_spec:
            amend_spec['label'] = config['label']
        amender = amenders[amend_spec['observance']]
        amendments.update(amender(amend_spec))

    return amendments

inventory = dict(
    days_weekly = dict(
        scheme = days_weekly_config_scheme,
        compiler = days_weekly_compiler,
        amender = days_weekly_amender,
    )
)

def validate_config(config, scheme):

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
    for param, specification in scheme['general'].items():
        value = validate_parameter(param, config, specification)
        config[param] = value
    for amend_spec in amend:
        for param, specification in scheme['amend'].items():
            value = validate_parameter(param, amend_spec, specification)
            amend_spec[param] = value

    config['amend'] = amend
    return config

def filter_amendments(amend, filter=None, required_keys=None):
    filter = dict() if filter is None else filter
    required_keys = [] if required_keys is None else required_keys
    filtered_amend=[]
    for amend_spec in amend:
        selected = True
        for filter_key, filter_values in filter.items():
            filter_values = to_iterable(filter_values)
            if filter_key in amend_spec:
                amend_spec_values = to_iterable(amend_spec[filter_key])
                value_found =  len(set(filter_values).intersection(amend_spec_values)) > 0
                selected = selected and value_found
        for required_key in required_keys:
            selected = selected and required_key in amend_spec
        if selected:
            filtered_amend.append(amend_spec)
    return filtered_amend


def from_config(config,
                  do_not_amend=False, only_custom_amendments=False,
                  amend_filter=None, required_amend_keys=None,
                  **custom_parameters):

    try:
        template = config['template']
    except KeyError:
        raise KeyError("Template is not specified in calendar config")
    scheme = inventory[template]['scheme']
    working_config = validate_config(config, scheme)
    tb_parameters = inventory[template]['compiler'](working_config, custom_parameters)

    tb_parameters['amendments'] = None
    if not do_not_amend:
        if 'amendments' in custom_parameters and not custom_parameters['amendments'] is None:
            custom_amendments = custom_parameters['amendments']
        else:
            custom_amendments = dict()
        if not only_custom_amendments:
            filtered_amend = filter_amendments(working_config['amend'],
                                               amend_filter, required_amend_keys)
            working_config['amend'] = filtered_amend
            tb_parameters['amendments'] = inventory[template]['amender'](working_config)

        # actually, amendments update may be tricky as two amendments may be keyed
        # by different time points within the same workshift
        freq = tb_parameters['base_unit_freq']
        tb_parameters['amendments'].update(
            {get_period(k, freq=freq).start_time: v
             for k, v in custom_amendments.items()}
        )

    return Timeboard(**tb_parameters)