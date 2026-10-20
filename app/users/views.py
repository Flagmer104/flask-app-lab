from flask import redirect, render_template, request, url_for

from app.users import users_bp


@users_bp.route("/hi/<name>")
def greetings(name):
    age = request.args.get("age", type=int)
    return render_template(
        "users/hi.html", page_title=f"Вітання, {name}", name=name.upper(), age=age
    )


@users_bp.route("/admin")
def admin():
    return redirect(url_for("users.greetings", name="administrator", age=45))
