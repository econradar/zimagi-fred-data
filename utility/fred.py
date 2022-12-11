from utility.data import load_json, get_identifier, clean_dict
from utility.time import Time

import urllib
import pandas
import time
import logging


logger = logging.getLogger(__name__)


class FredAPIError(ValueError):
    pass


class FredAPI(object):

    root_url = 'https://api.stlouisfed.org/fred'
    first_date = '1800-01-01'


    def __init__(self, command, api_key):
        self.command = command
        self.api_key = api_key

        self.time = Time(
            date_format = '%Y-%m-%d',
            time_format = '%H:%M:%S%z',
            spacer = ' '
        )
        self.lock_key = "fred_request_{}".format(
            get_identifier(self.api_key)
        )


    def get_category(self, category_id):
        data = self._fetch_data('category', category_id = category_id)
        if data is not None:
            category = data['categories'][0]
            if category['parent_id']:
                yield from self.get_category(category['parent_id'])
            yield category

    def get_child_categories(self, category_id = 0, recursive = True):
        data = self._fetch_data('category/children', category_id = category_id)
        if data is not None:
            for category in data['categories']:
                yield category
                if recursive:
                    yield from self.get_categories(category['id'], True)

    def get_series_categories(self, series_id, **params):
        params['series_id'] = series_id

        self._normalize_realtime_params(params)

        data = self._fetch_data('series/categories', **params)
        if data is not None:
            for category in data['categories']:
                if category['parent_id']:
                    yield from self.get_category(category['parent_id'])

                category['series'] = True
                yield category

    def get_category_tree(self, series_id, **params):
        id_map = {}

        for category in self.get_series_categories(series_id, **params):
            parent_id = category['parent_id']
            if parent_id not in id_map:
                id_map[parent_id] = []
            id_map[parent_id].append(category)

        def build_tree(data, category_id):
            for category in id_map.get(category_id, []):
                info = {
                    'id': category['id'],
                    'name': category['name'],
                    'notes': category.get('notes', None),
                    'children': []
                }
                build_tree(info['children'], category['id'])
                data.append(info)
            return data

        return build_tree([], 0)


    def get_series(self, series_id, return_list = False, **params):
        params['series_id'] = series_id

        self._normalize_realtime_params(params)

        results = list(self._get_series_data('series', **params))
        if not results:
            raise FredAPIError("No information exists for series id: {}".format(series_id))

        return results if return_list else results[0]

    def get_updated_series(self, start_time = None, end_time = None, limit = None, **params):
        params['limit'] = limit

        self._normalize_realtime_params(params)

        if start_time:
            if not isinstance(start_time, (str, int)):
                start_time = start_time.strftime('%Y%m%d%H%M')
            params['start_time'] = str(start_time)

        if end_time:
            if not isinstance(end_time, (str, int)):
                end_time = end_time.strftime('%Y%m%d%H%M')
            params['end_time'] = str(end_time)
        elif start_time:
            params['end_time'] = self.time.shift(self.time.now, 1, 'days').strftime('%Y%m%d%H%M')

        yield from self._get_series_data('series/updates', **params)

    def search_series(self, search_text = None, search_type = 'full_text', limit = None, **params):
        params['limit'] = limit

        self._normalize_sort_params(params)
        self._normalize_realtime_params(params)
        self._normalize_tag_params(params)

        if search_text:
            params['search_text'] = search_text
            params['search_type'] = search_type

        yield from self._get_series_data('series/search', **params)


    def get_revision_dates(self, series_id, **params):
        params['series_id'] = series_id

        self._normalize_sort_params(params, False, 'asc')
        self._normalize_realtime_params(params)

        return list(self._get_list_data('series/vintagedates', params, 'vintage_dates',
            max_page_size = 10000
        ))


    def get_data(self, series_id, observation_start = None, observation_end = None, limit = None, **params):
        params['series_id'] = series_id
        params['limit'] = limit

        self._normalize_sort_params(params, False, 'asc')
        self._normalize_realtime_params(params)

        if observation_start is not None:
            if not isinstance(observation_start, str):
                observation_start = observation_start.strftime('%Y-%m-%d')
            params['observation_start'] = observation_start

        if observation_end is not None:
            if not isinstance(observation_end, str):
                observation_end = observation_end.strftime('%Y-%m-%d')
            params['observation_end'] = observation_end

        yield from self._get_observation_data('series/observations', **params)


    def get_data_revisions(self, series_id, observation_start = None, observation_end = None, limit = None, **params):
        observation_start = self.time.to_datetime(observation_start if observation_start else self.first_date).date()
        observation_end = self.time.to_datetime(observation_end if observation_end else '9999-12-31').date()
        limit = None if not limit else limit

        count = 0
        revision_limit = 2000 # Hard limit of 2000 vintage dates / request

        revision_dates = self.get_revision_dates(series_id,
            realtime_start = self.first_date,
            realtime_end = '9999-12-31'
        )
        for revision_sequence in [
            revision_dates[index:index + revision_limit] for index in range(0, len(revision_dates), revision_limit)
        ]:
            start_date = self.time.to_datetime(revision_sequence[0])
            end_date = self.time.to_datetime(revision_sequence[-1])

            for observation in self.get_data(series_id,
                realtime_start = self.time.shift(start_date, -1 if count else 0, 'days'),
                realtime_end = end_date,
                limit = limit,
                **params
            ):
                realtime_start = self.time.to_datetime(observation['realtime_start'])

                if realtime_start >= start_date and realtime_start >= observation_start and realtime_start <= observation_end:
                    yield observation
                    if limit:
                        limit -= 1

            if limit == 0:
                break
            count += 1


    def _normalize_realtime_params(self, params):
        if 'realtime_start' in params and params['realtime_start'] and not isinstance(params['realtime_start'], str):
            params['realtime_start'] = params['realtime_start'].strftime('%Y-%m-%d')
        if 'realtime_end' in params and params['realtime_end'] and not isinstance(params['realtime_end'], str):
            params['realtime_end'] = params['realtime_end'].strftime('%Y-%m-%d')

    def _normalize_sort_params(self, params, order_by = True, default_sort = 'desc'):
        if order_by and 'order_by' not in params:
            params['order_by'] = 'popularity'
        if 'sort_order' not in params:
            params['sort_order'] = default_sort

    def _normalize_tag_params(self, params):
        if 'tag_names' in params and isinstance(params['tag_names'], (list, tuple)):
            params['tag_names'] = ";".join(params['tag_names'])
        if 'exclude_tag_names' in params and isinstance(params['exclude_tag_names'], (list, tuple)):
            params['exclude_tag_names'] = ";".join(params['exclude_tag_names'])


    def _fetch_data(self, path, **params):
        params['file_type'] = 'json'
        data = None

        safe_url = "{}/{}?{}".format(
            self.root_url,
            path,
            "&".join([ "{}={}".format(key, value) for key, value in clean_dict(params).items() ]
        ))
        url = "{}&api_key={}".format(safe_url, self.api_key)

        def load():
            nonlocal data
            try:
                time.sleep(1)
                logger.info("FRED request: {}".format(safe_url))
                response = urllib.request.urlopen(url)
                data = load_json(response.read())

            except urllib.error.HTTPError as e:
                logger.warning("FRED request {} failed with error: {}".format(path, e))
                data = load_json(e.read().decode('utf-8'))
                raise FredAPIError("{} ({})".format(data['error_message'], data['error_code']))

        self.command.run_exclusive(self.lock_key, load)
        return data


    def _get_list_data(self, path, params, element, limit = None, max_page_size = 1000, datetime_fields = None):
        page_size = min(limit, max_page_size) if limit else max_page_size
        if not datetime_fields:
            datetime_fields = []

        data = self._fetch_data(path, **{ **params, 'limit': page_size })
        count = len(data[element])

        for series in data[element]:
            for field in datetime_fields:
                if field in series:
                    series[field] = self._parse_datetime(series[field])
            yield series

        if count == page_size and (not limit or count < limit):
            params['offset'] = params.get('offset', 0) + page_size
            yield from self._get_list_data(path, params, element,
                limit = limit - count if limit else limit,
                max_page_size = max_page_size,
                datetime_fields = datetime_fields
            )


    def _get_series_data(self, path, limit = None, **params):
        yield from self._get_list_data(path, params, 'seriess',
            limit = limit,
            max_page_size = 1000,
            datetime_fields = [
                'realtime_start',
                'realtime_end',
                'observation_start',
                'observation_end',
                'last_updated'
            ]
        )

    def _get_observation_data(self, path, limit = None, **params):
        yield from self._get_list_data(path, params, 'observations',
            limit = limit,
            max_page_size = 100000,
            datetime_fields = [
                'realtime_start',
                'realtime_end',
                'date'
            ]
        )


    def _parse_datetime(self, date_time):
        if isinstance(date_time, str) and ':' in date_time:
            date_time += '00'
        return self.time.to_datetime(date_time)
