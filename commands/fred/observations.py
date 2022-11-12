from systems.commands.index import Command


class Observations(Command('fred.observations')):

    def exec(self):
        data = self.fred.get_series(self.indicator_id)
        self.notice(data)
