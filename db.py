"""
Database utility functions for executing queries and managing connections.
"""

import sqlite3

DB_PATH = "database.db"

def get_connection():
    """
    Establishes and returns a database connection with foreign key support.
    """
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=None):
    """
    Executes a SQL statement with optional parameters and commits the changes.
    """
    params = params or []
    con = get_connection()
    cur = con.execute(sql, params)
    con.commit()
    last_id = cur.lastrowid
    con.close()
    return last_id

def query(sql, params=None):
    """
    Executes a SQL query with optional parameters and returns the results.
    """
    params = params or []
    con = get_connection()
    rows = con.execute(sql, params).fetchall()
    con.close()
    return rows
