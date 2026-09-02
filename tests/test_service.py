import unittest
from io import BytesIO

from service import DateIconService, parse_date, parse_hex_color

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class ParseDateTests(unittest.TestCase):
    def test_valid_date_returns_day_month_tuple(self):
        self.assertEqual(parse_date("25_12"), (25, 12))

    def test_bad_format_non_numeric_raises(self):
        with self.assertRaises(ValueError):
            parse_date("abc")

    def test_bad_format_wrong_separator_raises(self):
        with self.assertRaises(ValueError):
            parse_date("1-2")

    def test_bad_format_missing_month_raises(self):
        with self.assertRaises(ValueError):
            parse_date("25")

    def test_month_zero_raises(self):
        with self.assertRaises(ValueError):
            parse_date("5_0")

    def test_month_thirteen_raises(self):
        with self.assertRaises(ValueError):
            parse_date("5_13")

    def test_day_zero_raises(self):
        with self.assertRaises(ValueError):
            parse_date("0_5")

    def test_day_thirty_two_raises(self):
        with self.assertRaises(ValueError):
            parse_date("32_5")


class ParseHexColorTests(unittest.TestCase):
    def test_accepts_leading_hash(self):
        self.assertEqual(parse_hex_color("#e38528"), (227, 133, 40))

    def test_accepts_no_leading_hash(self):
        self.assertEqual(parse_hex_color("e38528"), (227, 133, 40))

    def test_returns_three_int_tuple(self):
        result = parse_hex_color("e38528")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        self.assertTrue(all(isinstance(channel, int) for channel in result))


class DateIconServiceTests(unittest.TestCase):
    def test_generate_returns_bytesio_with_png_signature(self):
        result = DateIconService().generate("25_12")
        self.assertIsInstance(result, BytesIO)
        self.assertEqual(result.getvalue()[:8], PNG_SIGNATURE)

    def test_generate_unknown_theme_falls_back_to_default(self):
        default_bytes = DateIconService().generate("25_12", theme="default").getvalue()
        fallback_bytes = DateIconService().generate("25_12", theme="does-not-exist").getvalue()
        self.assertEqual(fallback_bytes[:8], PNG_SIGNATURE)
        self.assertEqual(fallback_bytes, default_bytes)


if __name__ == "__main__":
    unittest.main()
