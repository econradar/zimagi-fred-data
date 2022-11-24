from systems.commands.index import Command


class Series(Command('fred.series')):

    def exec(self):
        self.info(self.fred.search_by_category(18, order_by = 'popularity', sort_order = 'desc'))
