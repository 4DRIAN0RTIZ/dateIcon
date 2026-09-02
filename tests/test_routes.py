import unittest

from fastapi.testclient import TestClient

from app import app
from config import SIZES_ALLOWED

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

client = TestClient(app)


class RootEndpointTests(unittest.TestCase):
    def test_root_returns_endpoints_map(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("endpoints", body)
        endpoints = body["endpoints"]
        self.assertIsInstance(endpoints, dict)
        for key in ("/icon/{date}", "/themes", "/languages", "/sizes", "/health"):
            self.assertIn(key, endpoints)


class IconEndpointTests(unittest.TestCase):
    def test_valid_date_returns_png(self):
        response = client.get("/icon/25_12")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "image/png")
        self.assertTrue(response.content)
        self.assertTrue(response.content.startswith(PNG_SIGNATURE))

    def test_invalid_date_returns_400(self):
        response = client.get("/icon/99_99")
        self.assertEqual(response.status_code, 400)

    def test_allowed_size_returns_png(self):
        response = client.get("/icon/25_12?size=128")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "image/png")
        self.assertTrue(response.content.startswith(PNG_SIGNATURE))

    def test_disallowed_size_returns_400_listing_allowed_sizes(self):
        response = client.get("/icon/25_12?size=100")
        self.assertEqual(response.status_code, 400)
        detail = response.json()["detail"]
        self.assertIn(str(SIZES_ALLOWED), detail)
        self.assertIn("128", detail)
        self.assertIn("16", detail)

    def test_non_integer_size_returns_422(self):
        response = client.get("/icon/25_12?size=abc")
        self.assertEqual(response.status_code, 422)

    def test_custom_theme_valid_colors_returns_png(self):
        response = client.get(
            "/icon/25_12?theme=custom&bar_color=ff0000&bg_color=%23ffffff&text_color=000000"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "image/png")
        self.assertTrue(response.content.startswith(PNG_SIGNATURE))

    def test_custom_theme_invalid_color_returns_400(self):
        response = client.get("/icon/25_12?theme=custom&bar_color=xyz")
        self.assertEqual(response.status_code, 400)
        detail = response.json()["detail"]
        self.assertIn("xyz", detail)
        self.assertIn("hex", detail)

    def test_non_custom_theme_ignores_color_params(self):
        response = client.get("/icon/25_12?theme=default&bar_color=notacolor")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(PNG_SIGNATURE))

    def test_icon_has_cache_headers(self):
        response = client.get("/icon/25_12")
        self.assertEqual(response.status_code, 200)
        cache_control = response.headers["cache-control"].lower()
        self.assertIn("public", cache_control)
        self.assertIn("max-age=86400", cache_control)
        self.assertTrue(response.headers.get("etag"))

    def test_icon_same_query_same_etag(self):
        first = client.get("/icon/25_12?theme=ocean&size=128")
        second = client.get("/icon/25_12?theme=ocean&size=128")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.headers["etag"], second.headers["etag"])

    def test_icon_conditional_304(self):
        first = client.get("/icon/25_12")
        etag = first.headers["etag"]
        response = client.get("/icon/25_12", headers={"If-None-Match": etag})
        self.assertEqual(response.status_code, 304)
        self.assertEqual(response.content, b"")

    def test_icon_different_query_different_etag(self):
        first = client.get("/icon/25_12")
        second = client.get("/icon/26_12")
        self.assertNotEqual(first.headers["etag"], second.headers["etag"])


class MetadataEndpointTests(unittest.TestCase):
    def test_themes_returns_expected_key(self):
        response = client.get("/themes")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("themes", body)
        self.assertIn("default", body["themes"])

    def test_languages_returns_expected_key(self):
        response = client.get("/languages")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("languages", body)
        self.assertIn("es", body["languages"])

    def test_sizes_returns_expected_key(self):
        response = client.get("/sizes")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("sizes", body)
        self.assertIsInstance(body["sizes"], list)
        self.assertIn(64, body["sizes"])


class HealthEndpointTests(unittest.TestCase):
    def test_health_returns_ok(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
