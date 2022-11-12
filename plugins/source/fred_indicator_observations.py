from django.conf import settings

from systems.plugins.index import BaseProvider


class Provider(BaseProvider('source', 'fred_indicator_observations')):

    def item_columns(self):
        return [
            'source',
            'id',
            'date',
            'value'
        ]

    def load_fred_series(self, indicator_id, start_date, end_date):
        return self.fred.get_series(indicator_id,
            observation_start = start_date,
            observation_end = end_date
        )

    def load_item(self, data, context):
        record = data['record'].values
        return [
            settings.FRED_SOURCE_NAME,
            data['id'],
            record[0],
            record[1]
        ]
