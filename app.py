from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def resume():
    return render_template("resume.html", page_title="Резюме")


@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    form_submitted = request.method == "POST"
    return render_template(
        "contacts.html",
        page_title="Контакти",
        form_submitted=form_submitted,
    )


if __name__ == "__main__":
    app.run(debug=True)
