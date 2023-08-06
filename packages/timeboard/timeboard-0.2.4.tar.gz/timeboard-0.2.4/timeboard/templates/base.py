from timeboard.core import get_period, get_timestamp
from timeboard.utils import to_iterable, is_dict, is_string
from timeboard.exceptions import OutOfBoundsError
from timeboard.timeboard import Timeboard

import yaml
import abc, six
from collections import namedtuple

def collect_config(*configs):
    config = dict()
    for cfg in configs:
        if is_dict(cfg):
            config.update(cfg)
        else:
            if not is_string(cfg):
                raise TypeError("Config must be a dict or a filename. Got {}".
                                format(type(cfg)))
            with open(cfg, 'r') as f:
                config.update(yaml.load(f, Loader=yaml.SafeLoader))
    return config

@six.add_metaclass(abc.ABCMeta)
class TemplateMixin():

    @property
    @classmethod
    @abc.abstractmethod
    def _scheme(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def _validate(cls, config):
        pass

    @staticmethod
    def set_custom_bounds(config, custom_params):
        custom_start = config['start']
        custom_end = config['end']
        if 'start' in custom_params:
            start_ts = get_timestamp(custom_params['start'])
            if not config['start'] <=  start_ts <= config['end']:
                raise OutOfBoundsError("Point in time '{}' is outside the range [{}, {}] "
                    "of template {}".format(start_ts, config['start'],
                                            config['end'], config['template']))
            custom_start = start_ts
        if 'end' in custom_params:
            end_ts = get_timestamp(custom_params['end'])
            if not custom_start <=  end_ts <= config['end']:
                raise OutOfBoundsError("Point in time '{}' is outside the range [{}, {}] "
                    "of template {}".format(end_ts, custom_start,
                                            config['end'], config['template']))
            custom_end = end_ts
        updated_config = config.copy()
        updated_config['start'] = custom_start
        updated_config['end'] = custom_end
        return updated_config


    @classmethod
    @abc.abstractmethod
    def _compile(cls, config, custom_parameters):
        pass

    @classmethod
    @abc.abstractmethod
    def _amend(cls, config):
        pass


FilterCondition = namedtuple('FilterCondition', 'name values include required')


@six.add_metaclass(abc.ABCMeta)
class TimeboardFactory(object):

    def __init__(self, *configs):

        self._config = self._validate(collect_config(*configs))

    @property
    def config(self):
        return self._config

    # `_validate`, `_compile`, and `_amend` methods must be implemented in a Scheme mixin
    @abc.abstractmethod
    def _validate(self, config):
        pass

    @abc.abstractmethod
    def _compile(self, config, custom_parameters):
        pass

    @abc.abstractmethod
    def _amend(self, config):
        pass

    # _parse_kwargs will be propbably overriden in a derived class
    def _parse_amendment_specific_kwargs(self, config, kwargs):
        remaining_kwargs = kwargs.copy()
        amendment_filter = dict()
        do_not_observe = remaining_kwargs.pop('do_not_observe', [])
        if do_not_observe:
            amendment_filter['name'] = FilterCondition(name='name',
                                                       values=to_iterable(do_not_observe),
                                                       include=False,
                                                       required=False)

        # automatically extract scope keywords from config
        reserved_amend_keys = set(self._scheme['amend'].keys())
        scope_keys = set()
        for amend_spec in config['amend']:
            scope_keys |= set(amend_spec.keys()).difference(reserved_amend_keys)
        for scope_key in scope_keys:
            scope_value = remaining_kwargs.pop(scope_key, None)
            if scope_value is not None:
                amendment_filter[scope_key] = FilterCondition(name=scope_key,
                                                              values=to_iterable(scope_value),
                                                              include=True,
                                                              required=False)
        return amendment_filter, remaining_kwargs, config

    def _filter_amendments(self, amendment_specs, amendment_filter):
        """
        amendment_filter is {name:  FilterCondition}
        """
        amendment_filter = dict() if amendment_filter is None else amendment_filter
        filtered_amend_specs = []
        for amend_spec in amendment_specs:
            selected = True
            for filter_key, condition in amendment_filter.items():
                filter_values = to_iterable(condition.values)
                if filter_key in amend_spec:
                    amend_spec_values = to_iterable(amend_spec[filter_key])
                    value_found = len(set(filter_values).intersection(amend_spec_values)) > 0
                    selected = selected and (value_found == condition.include)
                elif condition.required:
                    selected = False
            if selected:
                filtered_amend_specs.append(amend_spec)
        return filtered_amend_specs


    def make_parameters(self, do_not_amend=False, only_custom_amendments=False,
             custom_amendments=None, **kwargs):

        # extract amendment conditions from **kwargs;
        # the rest is template-specific custom parameters for creating the Timeboard
        amendment_filter, remaining_kwargs, working_config = \
            self._parse_amendment_specific_kwargs(self._config, kwargs)

        # compile Timeboard() instantiation kwargs from template's defaults, template's config
        # and template-specific custom parameters supplied by the caller.
        # self._config may be modified in the process, so it is returned as well
        tb_parameters, remaining_kwargs, working_config = \
            self._compile(working_config, remaining_kwargs)

        # create amendments
        tb_parameters['amendments'] = None
        custom_amendments = dict() if custom_amendments is None else custom_amendments
        if not do_not_amend:
            if not only_custom_amendments and 'amend' in working_config:
                filtered_amend = self._filter_amendments(working_config['amend'],
                                                         amendment_filter)
                working_config['amend'] = filtered_amend
                tb_parameters['amendments'] = self._amend(working_config)

            freq = tb_parameters['base_unit_freq']
            tb_parameters['amendments'].update(
                {get_period(k, freq=freq).start_time: v
                 for k, v in custom_amendments.items()}
            )

        return tb_parameters

    def make(self, *args, **kwargs):
        tb_parameters = self.make_parameters(*args, **kwargs)
        return Timeboard(**tb_parameters)

    def __call__(self, *args, **kwargs):
        return self.make(*args, **kwargs)