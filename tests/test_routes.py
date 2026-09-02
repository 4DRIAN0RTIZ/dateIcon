import unittest

from fastapi.testclient import TestClient

from app import app

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
        for key in ("/icon/{date}", "/themes", "/languages", "/sizes"):
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
