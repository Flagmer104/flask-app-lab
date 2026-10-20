import unittest

from app import app


class PortfolioRoutesTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_resume_page_renders_required_content(self):
        response = self.client.get("/")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("<title>Резюме — Владислав Харків</title>", html)
        for section_id in (
            "about",
            "education",
            "skills",
            "technologies",
            "projects",
            "contact",
        ):
            self.assertIn(f'id="{section_id}"', html)
        self.assertIn('data-bs-target="#mainNavigation"', html)
        self.assertIn("Створено з Flask, Jinja2", html)
        self.assertIn("/static/images/profile-placeholder.svg", html)
        self.assertIn("/static/css/styles.css", html)

    def test_contacts_page_renders_form_and_github_link(self):
        response = self.client.get("/contacts")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("<title>Контакти — Владислав Харків</title>", html)
        self.assertIn("https://github.com/Flagmer104", html)
        self.assertIn('name="name"', html)
        self.assertIn('name="email"', html)
        self.assertIn('name="message"', html)

    def test_homepage_renders_from_package_structure(self):
        response = self.client.get("/homepage")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("<title>Головна — Владислав Харків</title>", html)
        self.assertIn("Один застосунок", html)

    def test_contact_post_shows_demo_feedback_without_echoing_data(self):
        private_value = "do-not-store-or-display"
        response = self.client.post(
            "/contacts",
            data={
                "name": private_value,
                "email": "student@example.com",
                "message": private_value,
            },
        )
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Повідомлення не було надіслано або збережено", html)
        self.assertNotIn(private_value, html)
        self.assertNotIn("student@example.com", html)

    def test_local_static_assets_load(self):
        for path, expected_type in (
            ("/static/css/styles.css", "text/css"),
            ("/static/images/profile-placeholder.svg", "image/svg+xml"),
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.content_type.startswith(expected_type))
                response.close()


if __name__ == "__main__":
    unittest.main()
