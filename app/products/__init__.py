from flask import Blueprint

products_bp = Blueprint(
    "products", __name__, template_folder="templates", url_prefix="/products"
)

from app.products import views  # noqa: E402, F401
