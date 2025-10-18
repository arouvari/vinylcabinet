"""
Script to seed the database with test data for users, albums, and reviews.
"""

import random
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM reviews")
db.execute("DELETE FROM albums")
db.execute("DELETE FROM users")

USER_COUNT = 100
ALBUM_COUNT = 1000
REVIEW_COUNT = 5000

for i in range(1, USER_COUNT + 1):
    db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
               (f"user{i}", "hashedpassword"))

for i in range(1, ALBUM_COUNT + 1):
    db.execute("""INSERT INTO albums (title, artist, year, genre, user_id, image_url)
                  VALUES (?, ?, ?, ?, ?, ?)""",
               (f"Album {i}", f"Artist {random.randint(1, 50)}",
                random.randint(1960, 2025),
                "Rock,Pop",
                random.randint(1, USER_COUNT),
                None))

used_pairs = set()
for _ in range(REVIEW_COUNT):
    while True:
        user_id = random.randint(1, USER_COUNT)
        album_id = random.randint(1, ALBUM_COUNT)
        pair = (album_id, user_id)
        if pair not in used_pairs:
            used_pairs.add(pair)
            stars = random.randint(1, 5)
            db.execute("INSERT INTO reviews (album_id, user_id, stars, text) VALUES (?, ?, ?, ?)",
                       (album_id, user_id, stars, f"Review for album {album_id} by user {user_id}"))
            break

db.commit()
db.close()
print("Test data added successfully!")
