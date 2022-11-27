from django.conf import settings

from systems.commands.index import CommandMixin
from utility.fred import FredAPI


class FREDSeriesMixin(CommandMixin('fred_series')):

    @property
    def fred(self):
        return FredAPI(self, settings.FRED_API_KEY)
