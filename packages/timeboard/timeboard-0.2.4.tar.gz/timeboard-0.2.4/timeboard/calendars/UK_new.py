from timeboard.templates.days_weekly import BusinessCalendarFactory
import os

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))

class Weekly8x5Factory(BusinessCalendarFactory):

    def __init__(self, *extra_configs):
        config_file = os.path.join(LOCAL_DIR, "uk_weekly_8x5.yaml")
        config_list = [config_file] + list(extra_configs)
        super(self.__class__, self).__init__(*config_list)

    # def _parse_scope_kwargs(self, kwargs):
    #     scope_filter = dict()
    #     remainig_kwargs = kwargs.copy()
    #     country = remainig_kwargs.pop('country', None)
    #     if country is not None:
    #         scope_filter['country'] = FilterCondition(name='country',
    #                                                   values=_to_iterable(country),
    #                                                   include=True,
    #                                                   required=False)
    #     return scope_filter, remainig_kwargs

Weekly8x5 = Weekly8x5Factory()


