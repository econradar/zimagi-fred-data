from django.conf import settings

from systems.plugins.index import ProviderMixin


class FREDUpdates(object):

    data = {}

    @classmethod
    def get_data(cls, fred, start_time):
        if start_time not in cls.data:
            cls.data[start_time] = list(fred.get_updated_series(start_time))
        return cls.data[start_time]


class FREDDataMixin(ProviderMixin('fred_data')):

    def get_start_date(self):
        date = self.field_date if self.field_date else self.field_start_date
        if not isinstance(date, str):
            date = date.strftime('%Y-%m-%d')
        return date


    def get_series_updates(self, start_time):
        if not isinstance(start_time, (str, int)):
            start_time = start_time.strftime('%Y%m%d%H%M')

        data = None

        def get_updates():
            nonlocal data
            data = FREDUpdates.get_data(self.fred, start_time)

        self.command.run_exclusive("fred_plugin_series_updates_{}".format(start_time), get_updates)
        return data
