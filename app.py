import hmac
import os
import sqlite3

from flask import Flask, Response, g, redirect, render_template, request, url_for


def create_app(database="signups.db"):
    app = Flask(__name__)
    app.config["DATABASE"] = database
    app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD")

    def is_admin():
        expected = app.config["ADMIN_PASSWORD"]
        auth = request.authorization
        if not expected or auth is None or auth.password is None:
            return False
        return hmac.compare_digest(auth.password.encode(), expected.encode())

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
        return g.db

    @app.teardown_appcontext
    def close_db(exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    with app.app_context():
        get_db().execute(
            "CREATE TABLE IF NOT EXISTS signups ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "name TEXT NOT NULL, email TEXT NOT NULL, major TEXT NOT NULL)"
        )

    @app.route("/", methods=["GET", "POST"])
    def signup():
        error = None
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            major = request.form.get("major", "").strip()
            if name and email and major:
                db = get_db()
                db.execute(
                    "INSERT INTO signups (name, email, major) VALUES (?, ?, ?)",
                    (name, email, major),
                )
                db.commit()
                return redirect(url_for("thanks"))
            error = "Please fill in every field."
        return render_template("signup.html", error=error), 400 if error else 200

    @app.route("/thanks")
    def thanks():
        return render_template("thanks.html")

    @app.route("/admin")
    def admin():
        if not is_admin():
            return Response(
                "Password required.",
                401,
                {"WWW-Authenticate": 'Basic realm="Trip signups admin"'},
            )
        signups = get_db().execute(
            "SELECT name, email, major FROM signups ORDER BY id"
        ).fetchall()
        return render_template("admin.html", signups=signups)

    return app
