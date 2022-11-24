from django.conf import settings

from systems.plugins.index import BaseProvider
from utility.fred import FredAPI


class Provider(BaseProvider('source', 'fred_indicator_categories')):

    def item_columns(self):
        return [
            'source',
            'id',
            'name',
            'parent_id'
        ]

    def load_items(self, context):
        fred = FredAPI(api_key = settings.FRED_API_KEY)

        def load_categories(category_id):
            self.command.info("Loading FRED categories for: {}".format(category_id))
            try:
                for category in fred.get_categories(category_id):
                    yield category
                    yield from load_categories(category['id'])
            except ValueError:
                pass
            self.command.sleep(1)

        yield from load_categories(0)

    def load_item(self, category, context):
        return [
            settings.FRED_SOURCE_NAME,
            category['id'],
            category['name'],
            category['parent_id'] if category['parent_id'] else None
        ]
