import argparse
import unittest

from qrng_demo import (
    get_python_random_counts,
    positive_int,
    summarize_bits,
)


class SummarizeBitsTests(unittest.TestCase):
    def test_balanced_sample_has_zero_statistic_and_unit_p_value(self):
        stats = summarize_bits(500, 500)

        self.assertEqual(stats.shots, 1000)
        self.assertEqual(stats.one_fraction, 0.5)
        self.assertEqual(stats.chi_squared, 0)
        self.assertEqual(stats.p_value, 1)

    def test_extreme_imbalance_has_small_p_value(self):
        stats = summarize_bits(10, 0)

        self.assertEqual(stats.chi_squared, 10)
        self.assertAlmostEqual(stats.p_value, 0.001565402, places=8)

    def test_empty_or_negative_counts_are_rejected(self):
        with self.assertRaises(ValueError):
            summarize_bits(0, 0)
        with self.assertRaises(ValueError):
            summarize_bits(-1, 2)

    def test_non_integer_counts_are_rejected(self):
        with self.assertRaises(TypeError):
            summarize_bits(1.5, 2)

    def test_python_comparison_is_reproducible_and_has_requested_length(self):
        first = get_python_random_counts(128, 19)
        second = get_python_random_counts(128, 19)

        self.assertEqual(first, second)
        self.assertEqual(sum(first), 128)


class ArgumentTests(unittest.TestCase):
    def test_shots_must_be_positive(self):
        self.assertEqual(positive_int("12"), 12)
        with self.assertRaises(argparse.ArgumentTypeError):
            positive_int("0")


if __name__ == "__main__":
    unittest.main()
