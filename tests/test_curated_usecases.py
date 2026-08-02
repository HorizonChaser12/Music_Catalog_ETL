import unittest

from curation.curated_usecases import get_release_year_summary_query


class CuratedUsecasesTests(unittest.TestCase):
    def test_release_year_summary_query_filters_blank_or_invalid_dates(self):
        sql = get_release_year_summary_query()
        self.assertIn("regexp_extract(trim(release_date)", sql)
        self.assertIn("trim(release_date) != ''", sql)
        self.assertIn("cast(regexp_extract(trim(release_date), '^(\\d{4})', 1) as int)", sql)


if __name__ == "__main__":
    unittest.main()
