from django.conf import settings
from fredapi import Fred

from systems.plugins.index import ProviderMixin
from utility.data import ensure_list

import datetime


class FREDSeriesMixin(ProviderMixin('fred_series')):

    def load_items(self, context):
        self.fred = Fred(api_key = settings.FRED_API_KEY)

        if not self.field_date or isinstance(self.field_date, str):
            date = self.field_date if self.field_date else self.field_start_date
            self.config['date'] = datetime.datetime.strptime(date, "%Y-%m-%d")
        if isinstance(self.field_date, datetime.datetime):
            self.config['date'] = self.field_date.date()

        current_date = datetime.datetime.now().date()
        time_period = datetime.timedelta(days = 2000)

        for indicator_id in ensure_list(self.field_indicator_ids):
            start_date = self.field_date
            end_date = start_date + time_period

            while True:
                self.command.info("Loading FRED indicator series: {} ({})".format(
                    indicator_id,
                    end_date.strftime("%Y-%m-%d")
                ))
                try:
                    data = self.load_fred_series(indicator_id,
                        start_date.strftime("%Y-%m-%d"),
                        end_date.strftime("%Y-%m-%d") if end_date < current_date else None
                    )
                except ValueError as error:
                    self.command.notice("No results")
                    data = None

                if data is not None and not data.empty:
                    for index, record in data.reset_index().iterrows():
                        yield {
                            'index': index,
                            'id': indicator_id,
                            'record': record
                        }

                if end_date >= current_date:
                    break
                else:
                    start_date = start_date + time_period
                    end_date = end_date + time_period


    def load_fred_series(self, indicator_id, start_date, end_date):
        # Override in subclass
        return None
