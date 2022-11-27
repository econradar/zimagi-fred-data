from django.conf import settings

from systems.plugins.index import ProviderMixin
from utility.fred import FredAPI


class FREDSeriesMixin(ProviderMixin('fred_series')):

    @property
    def fred(self):
        return FredAPI(self, settings.FRED_API_KEY)
