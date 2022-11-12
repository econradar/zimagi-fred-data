from django.conf import settings

from systems.plugins.index import BaseProvider


class Provider(BaseProvider('source', 'fred_indicator_revisions')):

    def item_columns(self):
        return [
            'source',
            'id',
            'date',
            'target_date',
            'value'
        ]

    def load_fred_series(self, indicator_id, start_date, end_date):
        return self.fred.get_series_all_releases(indicator_id,
            realtime_start = start_date,
            realtime_end = end_date
        )

    def load_item(self, data, context):
        record = data['record']
        return [
            settings.FRED_SOURCE_NAME,
            data['id'],
            record['realtime_start'],
            record['date'],
            record['value']
        ]
