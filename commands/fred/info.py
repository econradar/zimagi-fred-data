from systems.commands.index import Command
from utility.text import wrap_page


class Info(Command('fred.info')):

    def exec(self):
        data = self.fred.get_series_info(self.indicator_id)
        self.table(
            [ [ key, "\n".join(wrap_page(value)) ] for key, value in data.items() ],
            'fred_series_info'
        )
