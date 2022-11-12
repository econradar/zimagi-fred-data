from django.conf import settings
from fredapi import Fred

from systems.commands.index import CommandMixin


class FREDIndicatorMixin(CommandMixin('fred_indicator')):

    @property
    def fred(self):
        return Fred(api_key = settings.FRED_API_KEY)
