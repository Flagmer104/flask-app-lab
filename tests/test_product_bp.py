import unittest

from app import app


class ProductBlueprintTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def assert_product_detail(self, product_id, name, price, description):
        response = self.client.get(f"/products/{product_id}")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(name, html)
        self.assertIn(str(price), html)
        self.assertIn(description, html)

    def test_products_listing(self):
        response = self.client.get("/products/")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        for name, price in (("Laptop", 1200), ("Phone", 800), ("PC", 1800)):
            self.assertIn(name, html)
            self.assertIn(str(price), html)

    def test_laptop_detail(self):
        self.assert_product_detail(
            1,
            "Laptop",
            1200,
            "Потужний ноутбук з процесором Intel Core i7, 16 ГБ оперативної пам’яті та SSD на 512 ГБ.",
        )

    def test_phone_detail(self):
        self.assert_product_detail(
            2,
            "Phone",
            800,
            "Смартфон із 6.5-дюймовим OLED-дисплеєм, подвійною камерою та акумулятором на 5000 мА·год.",
        )

    def test_pc_detail(self):
        self.assert_product_detail(
            3,
            "PC",
            1800,
            "Настільний комп’ютер для ігор або роботи з графікою: RTX 4070, 32 ГБ RAM, 1 ТБ SSD.",
        )

    def test_invalid_product_returns_404(self):
        response = self.client.get("/products/999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
