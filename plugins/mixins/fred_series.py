from django.conf import settings

from systems.plugins.index import ProviderMixin
from utility.fred import FredAPI
from utility.time import Time


class FREDSeriesMixin(ProviderMixin('fred_series')):

    time = Time()


    @property
    def fred(self):
        if not getattr(self, '_fred_api', None):
            self._fred_api = FredAPI(self, settings.FRED_API_KEY)
        return self._fred_api


    def get_columns(self, *columns):
        return [ 'series_id', *columns ]

    def get_values(self, data, *columns):
        return [
            self.field_series_id,
            *[ data.get(column, None) for column in columns ]
        ]
