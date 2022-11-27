from systems.commands.index import Command


class Revisions(Command('fred.revisions')):

    def exec(self):
        self.render_results(self.fred.get_data_revisions(
            self.series_id,
            observation_start = self.start_time,
            observation_end = self.end_time,
            limit = self.limit,
            **self.api_params
        ))
