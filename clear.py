"""
Script to clear all data from the database.
"""

import sqlite3

db = sqlite3.connect("database.db")
db.execute("PRAGMA foreign_keys = ON")
db.execute("DELETE FROM reviews")
db.execute("DELETE FROM favorites")
db.execute("DELETE FROM album_genres")
db.execute("DELETE FROM user_profiles")
db.execute("DELETE FROM albums")
db.execute("DELETE FROM users")
db.commit()
db.close()