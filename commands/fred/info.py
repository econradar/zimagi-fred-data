from systems.commands.index import Command
from utility.text import wrap_page


class Info(Command('fred.info')):

    def exec(self):
        data = self.fred.get_series_info(self.indicator_id)

        self.notice("Meta Information")
        self.table(
            [ [ key, "\n".join(wrap_page(value)) ] for key, value in data.items() ],
            'fred_series_info'
        )

        categories = []
        for category in self.fred.get_series_categories(self.indicator_id):
            categories.append([ category['id'], category['name'], category['parent_id'] ])

        self.notice("Categories")
        self.table(
            categories,
            'fred_series_categories'
        )
