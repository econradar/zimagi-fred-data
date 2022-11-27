from systems.plugins.index import BaseProvider


class Provider(BaseProvider('source', 'fred_observations')):

    def item_columns(self):
        return self.get_columns('date', 'value')

    def load_items(self, context):
        start_date = self.get_start_date()

        self.command.info("Loading {} observations from {}".format(
            self.field_series_id,
            start_date
        ))
        yield from self.fred.get_data(
            self.field_series_id,
            observation_start = start_date
        )

    def load_item(self, observation, context):
        return self.get_values(observation, 'date', 'value')
