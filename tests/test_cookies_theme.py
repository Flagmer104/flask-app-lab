import unittest

from app import app


class CookieAndThemeTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        self.client.post(
            "/users/login",
            data={"username": "student", "password": "Lab4Demo2026!"},
        )

    def add_cookie(self, key="language", value="uk", lifetime="3600", **kwargs):
        return self.client.post(
            "/users/profile/cookies",
            data={
                "cookie_key": key,
                "cookie_value": value,
                "cookie_lifetime": lifetime,
            },
            **kwargs,
        )

    def test_add_cookie(self):
        response = self.add_cookie(follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Кукі «language» успішно додано".encode(), response.data)
        self.assertEqual(self.client.get_cookie("lab4_user_language").value, "uk")

    def test_delete_individual_cookie(self):
        self.add_cookie()
        response = self.client.post(
            "/users/profile/cookies/language/delete", follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Кукі «language» видалено".encode(), response.data)
        self.assertIsNone(self.client.get_cookie("lab4_user_language"))

    def test_delete_all_managed_cookies_preserves_session(self):
        self.add_cookie("language", "uk")
        self.add_cookie("layout", "compact")
        response = self.client.post(
            "/users/profile/cookies/delete-all", follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Видалено користувацьких кукі: 2".encode(), response.data)
        self.assertIsNone(self.client.get_cookie("lab4_user_language"))
        self.assertIsNone(self.client.get_cookie("lab4_user_layout"))
        self.assertIsNotNone(self.client.get_cookie(app.config["SESSION_COOKIE_NAME"]))

    def test_cookie_expiration_requires_valid_number(self):
        for invalid_lifetime in ("not-a-number", "0", "31536001"):
            with self.subTest(lifetime=invalid_lifetime):
                response = self.add_cookie(
                    lifetime=invalid_lifetime, follow_redirects=True
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn("Термін дії має бути числом".encode(), response.data)
                self.assertIsNone(self.client.get_cookie("lab4_user_language"))

    def test_profile_lists_only_managed_cookie_key_and_value(self):
        self.add_cookie("language", "uk")
        response = self.client.get("/users/profile")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"language", response.data)
        self.assertIn(b"uk", response.data)
        self.assertNotIn(b"lab4_user_language", response.data)

    def test_light_theme_selection(self):
        response = self.client.post(
            "/users/profile/theme/light", follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"profile-theme-light", response.data)
        self.assertEqual(self.client.get_cookie("lab4_theme").value, "light")

    def test_dark_theme_selection(self):
        response = self.client.post(
            "/users/profile/theme/dark", follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"profile-theme-dark", response.data)
        self.assertEqual(self.client.get_cookie("lab4_theme").value, "dark")

    def test_theme_persists_across_profile_requests(self):
        self.client.post("/users/profile/theme/dark")
        first = self.client.get("/users/profile")
        second = self.client.get("/users/profile")
        self.assertIn(b"profile-theme-dark", first.data)
        self.assertIn(b"profile-theme-dark", second.data)


if __name__ == "__main__":
    unittest.main()
