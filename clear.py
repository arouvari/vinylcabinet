import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM reviews")
db.execute("DELETE FROM albums")
db.execute("DELETE FROM users")
db.commit()
db.close()