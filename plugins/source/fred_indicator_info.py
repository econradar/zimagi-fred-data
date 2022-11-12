from django.conf import settings
from fredapi import Fred

from systems.plugins.index import BaseProvider
from utility.data import ensure_list


class Provider(BaseProvider('source', 'fred_indicator_info')):

    def item_columns(self):
        return [
            'source',
            'id',
            'realtime_start',
            'realtime_end',
            'title',
            'observation_start',
            'observation_end',
            'frequency',
            'frequency_short',
            'units',
            'units_short',
            'seasonal_adjustment',
            'seasonal_adjustment_short',
            'last_updated',
            'popularity',
            'notes'
        ]

    def load_items(self, context):
        fred = Fred(api_key = settings.FRED_API_KEY)
        for indicator_id in ensure_list(self.field_indicator_ids):
            self.command.info("Loading FRED indicator: {}".format(indicator_id))
            data = fred.get_series_info(indicator_id)
            if not data.empty:
                yield data.to_dict()

    def load_item(self, indicator, context):
        record = [ settings.FRED_SOURCE_NAME ]
        for field in self.item_columns()[1:]:
            record.append(indicator.get(field, None))
        return record
