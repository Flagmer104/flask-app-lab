import re

from flask import (
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.users import users_bp

DEMO_USERNAME = "student"
DEMO_PASSWORD = "Lab4Demo2026!"
MANAGED_COOKIE_PREFIX = "lab4_user_"
THEME_COOKIE_NAME = "lab4_theme"
COOKIE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
MAX_COOKIE_LIFETIME = 31_536_000


def _login_required():
    if "username" not in session:
        flash("Увійдіть, щоб відкрити профіль.", "error")
        return redirect(url_for("users.login"))
    return None


@users_bp.route("/hi/<name>")
def greetings(name):
    age = request.args.get("age", type=int)
    return render_template(
        "users/hi.html", page_title=f"Вітання, {name}", name=name.upper(), age=age
    )


@users_bp.route("/admin")
def admin():
    return redirect(url_for("users.greetings", name="administrator", age=45))


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == DEMO_USERNAME and password == DEMO_PASSWORD:
            session.clear()
            session.permanent = True
            session["username"] = username
            flash("Вхід виконано успішно. Ласкаво просимо!", "success")
            return redirect(url_for("users.profile"))

        flash("Невірне ім’я користувача або пароль.", "error")
        return redirect(url_for("users.login"))

    if "username" in session:
        return redirect(url_for("users.profile"))

    return render_template("users/login.html", page_title="Вхід")


@users_bp.route("/profile")
def profile():
    auth_redirect = _login_required()
    if auth_redirect is not None:
        return auth_redirect

    theme = request.cookies.get(THEME_COOKIE_NAME, "light")
    if theme not in {"light", "dark"}:
        theme = "light"

    managed_cookies = sorted(
        (
            (key.removeprefix(MANAGED_COOKIE_PREFIX), value)
            for key, value in request.cookies.items()
            if key.startswith(MANAGED_COOKIE_PREFIX)
        ),
        key=lambda item: item[0].lower(),
    )

    return render_template(
        "users/profile.html",
        page_title="Профіль",
        username=session["username"],
        managed_cookies=managed_cookies,
        theme=theme,
    )


@users_bp.route("/profile/cookies", methods=["POST"])
def add_cookie():
    auth_redirect = _login_required()
    if auth_redirect is not None:
        return auth_redirect

    key = request.form.get("cookie_key", "").strip()
    value = request.form.get("cookie_value", "").strip()
    lifetime_raw = request.form.get("cookie_lifetime", "").strip()

    if not COOKIE_NAME_PATTERN.fullmatch(key):
        flash(
            "Ключ кукі має містити 1–40 латинських літер, цифр, дефісів або підкреслень.",
            "error",
        )
        return redirect(url_for("users.profile"))

    if not value or len(value) > 200 or any(char in value for char in "\r\n;"):
        flash("Значення кукі має містити 1–200 безпечних символів.", "error")
        return redirect(url_for("users.profile"))

    try:
        lifetime = int(lifetime_raw)
    except ValueError:
        lifetime = 0

    if not 1 <= lifetime <= MAX_COOKIE_LIFETIME:
        flash("Термін дії має бути числом від 1 до 31536000 секунд.", "error")
        return redirect(url_for("users.profile"))

    response = make_response(redirect(url_for("users.profile")))
    response.set_cookie(
        f"{MANAGED_COOKIE_PREFIX}{key}",
        value,
        max_age=lifetime,
        httponly=True,
        samesite="Lax",
    )
    flash(f"Кукі «{key}» успішно додано.", "success")
    return response


@users_bp.route("/profile/cookies/<key>/delete", methods=["POST"])
def delete_cookie(key):
    auth_redirect = _login_required()
    if auth_redirect is not None:
        return auth_redirect

    if not COOKIE_NAME_PATTERN.fullmatch(key):
        flash("Некоректний ключ кукі.", "error")
        return redirect(url_for("users.profile"))

    full_key = f"{MANAGED_COOKIE_PREFIX}{key}"
    response = make_response(redirect(url_for("users.profile")))
    response.delete_cookie(full_key, httponly=True, samesite="Lax")
    if full_key in request.cookies:
        flash(f"Кукі «{key}» видалено.", "success")
    else:
        flash(f"Кукі «{key}» вже відсутнє.", "warning")
    return response


@users_bp.route("/profile/cookies/delete-all", methods=["POST"])
def delete_all_cookies():
    auth_redirect = _login_required()
    if auth_redirect is not None:
        return auth_redirect

    managed_keys = [
        key for key in request.cookies if key.startswith(MANAGED_COOKIE_PREFIX)
    ]
    response = make_response(redirect(url_for("users.profile")))
    for key in managed_keys:
        response.delete_cookie(key, httponly=True, samesite="Lax")

    if managed_keys:
        flash(f"Видалено користувацьких кукі: {len(managed_keys)}.", "success")
    else:
        flash("Немає користувацьких кукі для видалення.", "info")
    return response


@users_bp.route("/profile/theme/<theme>", methods=["POST"])
def change_theme(theme):
    auth_redirect = _login_required()
    if auth_redirect is not None:
        return auth_redirect

    if theme not in {"light", "dark"}:
        flash("Невідома кольорова схема.", "error")
        return redirect(url_for("users.profile"))

    response = make_response(redirect(url_for("users.profile")))
    response.set_cookie(
        THEME_COOKIE_NAME,
        theme,
        max_age=MAX_COOKIE_LIFETIME,
        httponly=True,
        samesite="Lax",
    )
    theme_label = "світлу" if theme == "light" else "темну"
    flash(f"Увімкнено {theme_label} тему профілю.", "success")
    return response


@users_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    flash("Ви успішно вийшли з профілю.", "info")
    return redirect(url_for("users.login"))
