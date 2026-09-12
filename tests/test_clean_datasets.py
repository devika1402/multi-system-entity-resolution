import unittest

import numpy as np
import pandas as pd

from clean_datasets import normalize_id, parse_dates, parse_mixed_amount


class CleanDatasetTests(unittest.TestCase):
    def test_parse_mixed_amount_formats(self):
        cases = {
            "€494,53": 494.53,
            "€1,984.31": 1984.31,
            "€1.696,47": 1696.47,
            "$1.456,38": 1456.38,
            "$925,28": 925.28,
            "€959.84": 959.84,
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertAlmostEqual(parse_mixed_amount(raw), expected)

    def test_parse_mixed_amount_keeps_missing_values(self):
        self.assertTrue(np.isnan(parse_mixed_amount(np.nan)))

    def test_parse_mixed_amount_keeps_numeric_precision(self):
        self.assertAlmostEqual(parse_mixed_amount(4137.46955765496), 4137.46955765496)

    def test_normalize_id_preserves_missing_values(self):
        result = normalize_id(pd.Series([" PAY0001 ", None]))
        self.assertEqual(result.iloc[0], "PAY0001")
        self.assertTrue(pd.isna(result.iloc[1]))

    def test_parse_dates_supports_mixed_stripe_formats(self):
        values = pd.Series(["March 01, 2025", "02/03/2025", "2025-03-05"])
        result = parse_dates(values, dayfirst=True)
        self.assertEqual(
            result.dt.strftime("%Y-%m-%d").tolist(),
            ["2025-03-01", "2025-03-02", "2025-03-05"],
        )


if __name__ == "__main__":
    unittest.main()
