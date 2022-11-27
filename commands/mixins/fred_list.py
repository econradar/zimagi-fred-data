from systems.commands.index import CommandMixin


class FREDListMixin(CommandMixin('fred_list')):

    def render_results(self, data_list):
        columns = self.display_fields
        data = []

        for item in data_list:
            record = []

            if not columns:
                columns = list(item.keys())

            for column in columns:
                record.append(item.get(column, None))

            data.append(record)

        self.table([ columns, *data ], 'fred_list_results')
