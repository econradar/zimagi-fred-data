from django.conf import settings

from systems.plugins.index import BaseProvider
from utility.fred import FredAPI


FRED_API_LOCK_KEY = 'fred_indicator_series_load'


class Provider(BaseProvider('source', 'fred_indicator_series')):

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
            'notes',
            'categories'
        ]

    def load_items(self, context):
        fred = FredAPI(api_key = settings.FRED_API_KEY)

        def load_category_items():
            series_collection = self._load_category(fred, self.field_category_id)

            for index, record in series_collection.iterrows():
                indicator_id = record['id']

                if int(record['popularity']) >= self.field_min_popularity:
                    self.command.info("Loading FRED indicator: {}".format(indicator_id))

                    data = self._load_series_info(fred, indicator_id)
                    if data and not data.empty:
                        data = data.to_dict()
                        data['categories'] = self._load_series_categories(fred, indicator_id)
                        yield data

        yield from load_category_items()

    def load_item(self, indicator, context):
        record = [ settings.FRED_SOURCE_NAME ]
        for field in self.item_columns()[1:]:
            record.append(indicator.get(field, None))
        return record


    def _load_category(self, fred, category_id):
        def load():
            self.command.sleep(1)
            return fred.search_by_category(
                category_id,
                order_by = 'popularity',
                sort_order = 'desc'
            )
        return self.command.run_exclusive(FRED_API_LOCK_KEY, load)

    def _load_series_info(self, fred, indicator_id):
        def load():
            self.command.sleep(1)
            return fred.get_series_info(indicator_id)

        return self.command.run_exclusive(FRED_API_LOCK_KEY, load)

    def _load_series_categories(self, fred, indicator_id):
        def load():
            self.command.sleep(1)
            return [ category['id'] for category in fred.get_series_categories(indicator_id) ]

        return self.command.run_exclusive(FRED_API_LOCK_KEY, load)
