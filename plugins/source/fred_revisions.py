from systems.plugins.index import BaseProvider


class Provider(BaseProvider('source', 'fred_revisions')):

    def item_columns(self):
        return self.get_columns('date', 'target_date', 'value')

    def load_fred_series(self, indicator_id, start_date, end_date):
        start_date = self.get_start_date()

        self.command.info("Loading FRED series {} revisions from {}".format(
            self.field_series_id,
            start_date
        ))
        yield from self.fred.get_data_revisions(
            self.field_series_id,
            observation_start = start_date
        )

    def load_item(self, revision, context):
        return self.get_values(revision, 'realtime_start', 'date', 'value')
