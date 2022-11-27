from systems.plugins.index import BaseProvider


class Provider(BaseProvider('source', 'fred_revisions')):

    def item_columns(self):
        return self.get_columns('date', 'target_date', 'value')

    def load_items(self, context):
        yield from self.fred.get_data_revisions(
            self.field_series_id,
            observation_start = self.get_start_date()
        )

    def load_item(self, revision, context):
        return self.get_values(revision, 'realtime_start', 'date', 'value')
