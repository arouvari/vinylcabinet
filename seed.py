import random
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM reviews")
db.execute("DELETE FROM albums")
db.execute("DELETE FROM users")

user_count = 100
album_count = 1000
review_count = 5000

for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
               (f"user{i}", "hashedpassword"))

for i in range(1, album_count + 1):
    db.execute("""INSERT INTO albums (title, artist, year, genre, user_id, image_url)
                  VALUES (?, ?, ?, ?, ?, ?)""",
               (f"Album {i}", f"Artist {random.randint(1, 50)}",
                random.randint(1960, 2025),
                "Rock,Pop",
                random.randint(1, user_count),
                None))

used_pairs = set()
for _ in range(review_count):
    while True:
        user_id = random.randint(1, user_count)
        album_id = random.randint(1, album_count)
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
