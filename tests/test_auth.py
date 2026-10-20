import unittest

from app import app


class AuthenticationTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def login(self, username="student", password="Lab4Demo2026!", **kwargs):
        return self.client.post(
            "/users/login",
            data={"username": username, "password": password},
            **kwargs,
        )

    def test_login_page_is_available(self):
        response = self.client.get("/users/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="username"', response.data)
        self.assertIn(b'name="password"', response.data)

    def test_successful_authentication_sets_session(self):
        response = self.login()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/users/profile"))
        with self.client.session_transaction() as user_session:
            self.assertEqual(user_session["username"], "student")

    def test_incorrect_credentials_do_not_authenticate(self):
        response = self.login(password="wrong", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Невірне ім’я користувача або пароль".encode(), response.data)
        with self.client.session_transaction() as user_session:
            self.assertNotIn("username", user_session)

    def test_session_persists_between_requests(self):
        self.login()
        first = self.client.get("/users/profile")
        second = self.client.get("/users/profile")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)

    def test_protected_profile_redirects_to_login(self):
        response = self.client.get("/users/profile", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Увійдіть, щоб відкрити профіль".encode(), response.data)

    def test_profile_displays_session_username(self):
        self.login()
        response = self.client.get("/users/profile")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"student", response.data)
        self.assertIn("Авторизовано".encode(), response.data)

    def test_logout_clears_authentication(self):
        self.login()
        response = self.client.post("/users/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ви успішно вийшли".encode(), response.data)
        with self.client.session_transaction() as user_session:
            self.assertNotIn("username", user_session)

    def test_success_flash_is_displayed_after_redirect(self):
        response = self.login(follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Вхід виконано успішно".encode(), response.data)
        self.assertIn(b"alert-success", response.data)


if __name__ == "__main__":
    unittest.main()
