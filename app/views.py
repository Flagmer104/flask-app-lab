from flask import render_template, request

from app import app


@app.route("/")
def resume():
    return render_template("resume.html", page_title="Резюме")


@app.route("/homepage")
def homepage():
    return render_template("homepage.html", page_title="Головна")


@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    form_submitted = request.method == "POST"
    return render_template(
        "contacts.html",
        page_title="Контакти",
        form_submitted=form_submitted,
    )
