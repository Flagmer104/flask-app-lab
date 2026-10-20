from flask import Flask

app = Flask(__name__)

# Import routes only after the Flask instance exists to avoid circular imports.
from app import views  # noqa: E402, F401
