from fredapi import Fred


class FredAPI(Fred):

    def get_categories(self, category_id = 0):
        url = "%s/category/children?category_id=%s" % (self.root_url, category_id)
        root = self._Fred__fetch_data(url)
        categories = []

        if root is not None:
            for child in root:
                categories.append(child.attrib)
        return categories


    def get_series_categories(self, series_id):
        url = "%s/series/categories?series_id=%s" % (self.root_url, series_id)
        root = self._Fred__fetch_data(url)
        categories = []

        if root is not None:
            for child in root:
                categories.append(child.attrib)
        return categories
