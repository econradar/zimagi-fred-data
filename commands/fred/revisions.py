from systems.commands.index import Command


class Revisions(Command('fred.revisions')):

    def exec(self):
        data = self.fred.get_series_all_releases(self.indicator_id)
        self.notice(data)
