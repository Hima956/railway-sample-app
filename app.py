import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DB_NAME = "tasks.db"


def init_db():
    """Create the tasks table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title")
    if title:
        conn = get_db_connection()
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, 0)", (title,))
        conn.commit()
        conn.close()
    return redirect(url_for("index"))


@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/health")
def health():
    """Simple health check endpoint - useful for Railway to verify the app is alive."""
    return {"status": "ok"}


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
else:
    # Ensure DB is initialized even when run via gunicorn
    init_db()