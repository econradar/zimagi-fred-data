from systems.commands.index import Command


class Search(Command('fred.series.search')):

    def exec(self):
        self.render_results(self.fred.search_series(
            self.search_text,
            self.search_type,
            limit = self.limit,
            **self.api_params
        ))
