from systems.plugins.index import BaseProvider


class Provider(BaseProvider('source', 'fred_series')):

    category_columns = [
        'id',
        'name',
        'parent_id',
        'notes'
    ]
    series_columns = [
        'title',
        'realtime_start',
        'realtime_end',
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

    def item_columns(self):
        return {
            'category': self.get_columns(*self.category_columns),
            'series': self.get_columns(*self.series_columns)
        }

    def load_items(self, context):
        yield {
            'info': self.fred.get_series(self.field_series_id),
            'categories': list(self.fred.get_series_categories(self.field_series_id))
        }

    def load_item(self, series_info, context):
        series = series_info['info']
        series['categories'] = []

        categories = []
        for category in series_info['categories']:
            categories.append(self.get_values(category, *self.category_columns))
            if 'series' in category and category['series']:
                series['categories'].append(category['id'])

        return {
            'category': categories,
            'series': self.get_values(series, *self.series_columns)
        }
