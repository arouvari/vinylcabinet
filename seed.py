"""
Script to seed the database with test data for users, albums, and reviews.
"""

import random
import sqlite3

db = sqlite3.connect("database.db")
db.execute("PRAGMA foreign_keys = ON")
db.execute("DELETE FROM reviews")
db.execute("DELETE FROM favorites")
db.execute("DELETE FROM album_genres")
db.execute("DELETE FROM user_profiles")
db.execute("DELETE FROM albums")
db.execute("DELETE FROM users")

USER_COUNT = 100000
ALBUM_COUNT = 1000000
REVIEW_COUNT = 5000000

for i in range(1, USER_COUNT + 1):
    db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
               (f"user{i}", "hashedpassword"))


genres = db.execute("SELECT id FROM genres").fetchall()
genre_ids = [g[0] for g in genres]

for i in range(1, ALBUM_COUNT + 1):
    album_id = db.execute("""
        INSERT INTO albums (title, artist, year, genre, user_id, image_url)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        f"Album {i}",
        f"Artist {random.randint(1, 50)}",
        str(random.randint(1960, 2025)),
        "",
        random.randint(1, USER_COUNT),
        None
    )).lastrowid

    num_genres = random.randint(1, 3)
    selected_genres = random.sample(genre_ids, min(num_genres, len(genre_ids)))
    for genre_id in selected_genres:
        db.execute(
            "INSERT INTO album_genres (album_id, genre_id) VALUES (?, ?)",
            (album_id, genre_id)
        )

used_pairs = set()
for _ in range(REVIEW_COUNT):
    while True:
        user_id = random.randint(1, USER_COUNT)
        album_id = random.randint(1, ALBUM_COUNT)
        pair = (album_id, user_id)
        if pair not in used_pairs:
            used_pairs.add(pair)
            stars = random.randint(1, 5)
            db.execute(
                "INSERT INTO reviews (album_id, user_id, stars, text) VALUES (?, ?, ?, ?)",
                (album_id, user_id, stars, f"Review for album {album_id} by user {user_id}")
            )
            break

for i in range(1, USER_COUNT + 1):
    if random.random() < 0.3:
        db.execute("""
            INSERT INTO user_profiles (user_id, bio, location, favorite_genre_id)
            VALUES (?, ?, ?, ?)
        """, (
            i,
            f"This is user {i}'s bio",
            random.choice(["Helsinki", "Tampere", "Turku", "Oulu", None]),
            random.choice(genre_ids) if random.random() < 0.5 else None
        ))

for _ in range(500):
    try:
        db.execute(
            "INSERT INTO favorites (user_id, album_id) VALUES (?, ?)",
            (random.randint(1, USER_COUNT), random.randint(1, ALBUM_COUNT))
        )
    except sqlite3.IntegrityError:
        pass

db.commit()
db.close()
print("Test data added successfully!")
