from django.conf import settings

from systems.plugins.index import ProviderMixin


class FREDDataMixin(ProviderMixin('fred_data')):

    def get_columns(self, *columns):
        return [ 'source', 'series_id', *columns ]

    def get_values(self, data, *columns):
        return [
            settings.FRED_SOURCE_NAME,
            self.field_series_id,
            *[ data.get(column, None) for column in columns ]
        ]


    def get_start_date(self):
        date = self.field_date if self.field_date else self.field_start_date
        if not isinstance(date, str):
            date = date.strftime('%Y-%m-%d')
        return date
