from django.conf import settings

from systems.commands.index import CommandMixin
from utility.fred import FredAPI


class FREDIndicatorMixin(CommandMixin('fred_indicator')):

    @property
    def fred(self):
        return FredAPI(api_key = settings.FRED_API_KEY)
