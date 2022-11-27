from systems.commands.index import Command


class Updates(Command('fred.series.updates')):

    def exec(self):
        self.render_results(self.fred.get_updated_series(
            self.start_time,
            self.end_time,
            limit = self.limit,
            **self.api_params
        ))
