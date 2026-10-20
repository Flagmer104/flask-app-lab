from flask import flash, redirect, render_template, request, session, url_for

from app.users import users_bp

DEMO_USERNAME = "student"
DEMO_PASSWORD = "Lab4Demo2026!"


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

    return render_template(
        "users/profile.html",
        page_title="Профіль",
        username=session["username"],
    )


@users_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    flash("Ви успішно вийшли з профілю.", "info")
    return redirect(url_for("users.login"))
