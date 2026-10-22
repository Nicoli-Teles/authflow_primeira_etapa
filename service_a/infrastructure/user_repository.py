import os
import sqlite3
from domain.user import User

class SQLiteUserRepository:
    def __init__(self):
        self.path = os.getenv("DATABASE_PATH", "/data/users.db")
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        return db
    def find_by_email(self, email):
        with self.connect() as db:
            row = db.execute("SELECT id,name,email,password_hash FROM users WHERE email=?", (email,)).fetchone()
            return User(row["id"], row["name"], row["email"], row["password_hash"]) if row else None
    def create(self, name, email, password_hash):
        with self.connect() as db:
            cur = db.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)", (name,email,password_hash))
            return User(cur.lastrowid, name, email, password_hash)
