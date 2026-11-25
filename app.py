"""Shopping List Manager: a small Flask and SQLite learning application."""
import os
import re
import sqlite3
from functools import wraps
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from database import close_db, get_db, init_db


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "development-only-change-me"),
        DATABASE=str(Path(app.instance_path) / "shopping.sqlite3"),
    )
    if test_config:
        app.config.update(test_config)
    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()

    def login_required(view):
        @wraps(view)
        def protected(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            return view(*args, **kwargs)
        return protected

    def owned_list(list_id):
        return get_db().execute(
            "SELECT id, name, store FROM shopping_lists WHERE id=? AND user_id=?",
            (list_id, session["user_id"]),
        ).fetchone()

    @app.route("/")
    def index():
        return redirect(url_for("lists") if "user_id" in session else url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            if len(username) < 3 or len(password) < 8:
                flash("Username must have 3+ characters and password 8+ characters.")
            else:
                try:
                    db = get_db()
                    db.execute("INSERT INTO users(username, password_hash) VALUES (?, ?)",
                               (username, generate_password_hash(password)))
                    db.commit()
                    flash("Account created. Sign in to continue.")
                    return redirect(url_for("login"))
                except sqlite3.IntegrityError:
                    flash("Username already exists.")
        return render_template("auth.html", mode="register")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = get_db().execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
            if user and check_password_hash(user["password_hash"], password):
                session.clear()
                session["user_id"] = user["id"]
                session["username"] = username
                return redirect(url_for("lists"))
            flash("Invalid username or password.")
        return render_template("auth.html", mode="login")

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/lists", methods=["GET", "POST"])
    @login_required
    def lists():
        db = get_db()
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            store = request.form.get("store", "").strip()
            if not name:
                flash("Enter a list name.")
            else:
                db.execute("INSERT INTO shopping_lists(user_id, name, store) VALUES (?, ?, ?)",
                           (session["user_id"], name, store))
                db.commit()
                return redirect(url_for("lists"))
        rows = db.execute("SELECT * FROM shopping_lists WHERE user_id=? ORDER BY id DESC",
                          (session["user_id"],)).fetchall()
        return render_template("lists.html", lists=rows)

    @app.route("/lists/<int:list_id>")
    @login_required
    def list_details(list_id):
        shopping_list = owned_list(list_id)
        if shopping_list is None:
            return "List not found.", 404
        rows = get_db().execute("SELECT * FROM list_items WHERE list_id=? ORDER BY id DESC",
                                (list_id,)).fetchall()
        total_cents = sum(item["quantity"] * item["price_cents"] for item in rows)
        return render_template("details.html", shopping_list=shopping_list,
                               items=rows, total=total_cents / 100)

    @app.post("/lists/<int:list_id>/items")
    @login_required
    def add_item(list_id):
        if owned_list(list_id) is None:
            return "List not found.", 404
        name = request.form.get("name", "").strip()
        barcode = request.form.get("barcode", "").strip()
        try:
            quantity = int(request.form.get("quantity", "0"))
            price_str = request.form.get("price", "").strip()
            if not re.fullmatch(r"\d+(?:\.\d{1,2})?", price_str):
                raise ValueError()
            whole, _, fractional = price_str.partition(".")
            price_cents = int(whole) * 100 + int(fractional.ljust(2, "0")) if fractional else int(whole)*100
            if not name or quantity <= 0:
                raise ValueError()
        except ValueError:
            flash("Enter a name, positive quantity, and valid price (e.g. 12.50).")
            return redirect(url_for("list_details", list_id=list_id))
        db = get_db()
        db.execute("INSERT INTO list_items(list_id, name, barcode, quantity, price_cents) "
                   "VALUES (?, ?, ?, ?, ?)", (list_id, name, barcode, quantity, price_cents))
        db.commit()
        return redirect(url_for("list_details", list_id=list_id))

    @app.post("/lists/<int:list_id>/items/<int:item_id>/delete")
    @login_required
    def delete_item(list_id, item_id):
        if owned_list(list_id) is None:
            return "List not found.", 404
        db = get_db()
        db.execute("DELETE FROM list_items WHERE id=? AND list_id=?", (item_id, list_id))
        db.commit()
        return redirect(url_for("list_details", list_id=list_id))

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
