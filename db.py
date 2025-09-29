import sqlite3

DB_PATH = "database.db"

def get_connection():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=None):
    params = params or []
    con = get_connection()
    cur = con.execute(sql, params)
    con.commit()
    last_id = cur.lastrowid
    con.close()
    return last_id

def query(sql, params=None):
    params = params or []
    con = get_connection()
    rows = con.execute(sql, params).fetchall()
    con.close()
    return rows
