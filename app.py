import os
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, request, g, render_template, send_file

DB_PATH = os.environ.get("DB_PATH", "/data/shelf.db")
BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
LOGO_PATH = os.environ.get("LOGO_PATH", "")

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as f:
    APP_VERSION = f.read().strip()

app = Flask(__name__)


def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
    return db


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT,
            status TEXT NOT NULL DEFAULT 'available',
            holder TEXT,
            since TEXT
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT NOT NULL,
            action TEXT NOT NULL,
            actor_name TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (book_id) REFERENCES books (id)
        )
        """
    )
    count = db.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    if count == 0:
        seed = [
            ("SVI-01", "Le 7 regole per avere successo", "Stephen Covey"),
            ("SVI-02", "Intelligenza emotiva", "Daniel Goleman"),
            ("SVI-03", "Le abitudini atomiche", "James Clear"),
            ("NAR-01", "Se questo è un uomo", "Primo Levi"),
            ("NAR-02", "Il nome della rosa", "Umberto Eco"),
            ("NAR-03", "Le otto montagne", "Paolo Cognetti"),
        ]
        db.executemany(
            "INSERT INTO books (id, title, author, status) VALUES (?, ?, ?, 'available')",
            seed,
        )
        db.commit()
    db.close()


def next_free_id(db):
    rows = db.execute("SELECT id FROM books WHERE id LIKE 'LIB-%'").fetchall()
    nums = []
    for r in rows:
        try:
            nums.append(int(r["id"].split("-")[1]))
        except (IndexError, ValueError):
            continue
    n = max(nums) + 1 if nums else 1
    return f"LIB-{n:02d}"


@app.route("/")
def index():
    return render_template("index.html", base_url=BASE_URL, version=APP_VERSION)


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")


@app.route("/logo")
def logo():
    if not LOGO_PATH or not os.path.isfile(LOGO_PATH):
        return jsonify({"error": "not_found"}), 404
    return send_file(LOGO_PATH)


@app.route("/api/version", methods=["GET"])
def version():
    return jsonify({"version": APP_VERSION})


@app.route("/api/books", methods=["GET"])
def list_books():
    db = get_db()
    rows = db.execute("SELECT * FROM books ORDER BY id").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/books", methods=["POST"])
def create_book():
    data = request.get_json(force=True, silent=True) or {}
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()
    if not title:
        return jsonify({"error": "title_required"}), 400
    db = get_db()
    new_id = next_free_id(db)
    db.execute(
        "INSERT INTO books (id, title, author, status) VALUES (?, ?, ?, 'available')",
        (new_id, title, author),
    )
    db.commit()
    row = db.execute("SELECT * FROM books WHERE id = ?", (new_id,)).fetchone()
    return jsonify(dict(row)), 201


@app.route("/api/books/<book_id>/checkout", methods=["POST"])
def checkout_book(book_id):
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip() or None
    db = get_db()
    row = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if row is None:
        return jsonify({"error": "not_found"}), 404
    if row["status"] == "checked_out":
        return jsonify({"error": "already_checked_out"}), 409
    now = datetime.utcnow().isoformat()
    db.execute(
        "UPDATE books SET status = 'checked_out', holder = ?, since = ? WHERE id = ?",
        (name, now, book_id),
    )
    db.execute(
        "INSERT INTO logs (book_id, action, actor_name, timestamp) VALUES (?, 'checkout', ?, ?)",
        (book_id, name, now),
    )
    db.commit()
    row = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    return jsonify(dict(row))


@app.route("/api/books/<book_id>/checkin", methods=["POST"])
def checkin_book(book_id):
    db = get_db()
    row = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if row is None:
        return jsonify({"error": "not_found"}), 404
    if row["status"] == "available":
        return jsonify({"error": "already_available"}), 409
    now = datetime.utcnow().isoformat()
    db.execute(
        "UPDATE books SET status = 'available', holder = NULL, since = NULL WHERE id = ?",
        (book_id,),
    )
    db.execute(
        "INSERT INTO logs (book_id, action, actor_name, timestamp) VALUES (?, 'checkin', ?, ?)",
        (book_id, row["holder"], now),
    )
    db.commit()
    row = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    return jsonify(dict(row))


@app.route("/api/logs", methods=["GET"])
def list_logs():
    limit = request.args.get("limit", default=30, type=int)
    db = get_db()
    rows = db.execute(
        """
        SELECT logs.id, logs.book_id, books.title AS book_title,
               logs.action, logs.actor_name, logs.timestamp
        FROM logs
        LEFT JOIN books ON books.id = logs.book_id
        ORDER BY logs.id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return jsonify([dict(r) for r in rows])


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
