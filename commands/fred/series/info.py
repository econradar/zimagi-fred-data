from systems.commands.index import Command
from utility.text import wrap_page


class Info(Command('fred.series.info')):

    def exec(self):
        data = self.fred.get_series(self.series_id)

        self.notice("Meta Information")
        self.table(
            [ [ key, "\n".join(wrap_page(value)) ] for key, value in data.items() ],
            'fred_series_info'
        )

        self.notice("Categories")
        self.render_categories(self.fred.get_category_tree(self.series_id))


    def render_categories(self, category_tree, prefix = ''):
        notes_prefix = "{}   ".format(prefix)

        self.info('')

        for category in category_tree:
            self.data("{} * {}".format(prefix, self.key_color(category['name'])), category['id'])
            if category['notes']:
                self.info('')
                self.info("\n".join(wrap_page(category['notes'], init_indent = notes_prefix, indent = notes_prefix)).rstrip())

            self.render_categories(category['children'], "    {}".format(prefix))
