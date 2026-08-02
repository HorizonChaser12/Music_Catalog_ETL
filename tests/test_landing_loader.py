import unittest

from loading.load_tables_landing import build_insert_sql


class LandingLoaderSqlTests(unittest.TestCase):
    def test_uses_composite_conflict_target_for_landing_tables(self):
        sql = build_insert_sql(
            columns=["id", "payload", "etl_batch_id", "created_at", "updated_at"],
            schema_name="landing",
            table_name="lnd_artists",
        )

        self.assertIn("ON CONFLICT (id, etl_batch_id) DO UPDATE SET", sql)
        self.assertNotIn("ON CONFLICT (id) DO UPDATE SET", sql)


if __name__ == "__main__":
    unittest.main()
