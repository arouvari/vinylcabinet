"""
Database operations for the Vinyl Cabinet application.
Handles CRUD operations for albums, genres, reviews, and user statistics.
"""

from db import query, execute

def add_album(title, artist, year, genre_ids, user_id, image_url=None):
    """
    Adds a new album to the database.
    """
    try:
        album_id = execute(
            "INSERT INTO albums (title, artist, year, genre, user_id, image_url) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (title, artist, year, '', user_id, image_url or None)
        )
        if genre_ids:
            assign_genres_to_album(album_id, genre_ids)
        return True, "Album added successfully."
    except Exception as e:
        return False, str(e)

def update_album(album_id, title, artist, year, genre_ids, image_url=None):
    """
    Updates an existing album in the database.
    """
    execute("""
        UPDATE albums SET title = ?, artist = ?, year = ?, genre = ?, image_url = ?
        WHERE id = ?
    """, (title, artist, year, '', image_url or None, album_id))
    assign_genres_to_album(album_id, genre_ids)

def delete_album(album_id):
    """
    Deletes an album from the database.
    """
    execute("DELETE FROM albums WHERE id = ?", (album_id,))

def get_all_genres():
    """
    Fetches all available genres from the database.
    """
    rows = query("SELECT id, name FROM genres ORDER BY name")
    return [dict(row) for row in rows]

def assign_genres_to_album(album_id, genre_ids):
    """
    Assigns genres to an album.
    """
    execute("DELETE FROM album_genres WHERE album_id = ?", (album_id,))
    for genre_id in genre_ids:
        execute(
            "INSERT INTO album_genres (album_id, genre_id) VALUES (?, ?)",
            (album_id, genre_id)
        )

def get_album_genres(album_id):
    """
    Fetches genres for a specific album.
    """
    rows = query("""
        SELECT g.id, g.name
        FROM genres g
        JOIN album_genres ag ON g.id = ag.genre_id
        WHERE ag.album_id = ?
        ORDER BY g.name
    """, (album_id,))
    return [dict(row) for row in rows]

def validate_album_data(data):
    """
    Validates album data for required fields and formats.
    """
    errors = {}
    if not data.get("title"):
        errors["title"] = "Title is required."
    if not data.get("artist"):
        errors["artist"] = "Artist is required."
    if not data.get("year") or not data["year"].isdigit():
        errors["year"] = "Year must be a number."
    if not data.get("genres", []):
        errors["genres"] = "At least one genre is required."
    return errors

def search_albums(query_text, user_id=None):
    """
    Searches albums based on title, artist, or genre.
    """
    sql = """
        SELECT DISTINCT a.id, a.title, a.artist, a.year, a.image_url, u.username AS owner_username
        FROM albums a
        JOIN users u ON a.user_id = u.id
        LEFT JOIN album_genres ag ON a.id = ag.album_id
        LEFT JOIN genres g ON ag.genre_id = g.id
        WHERE a.title LIKE ? OR a.artist LIKE ? OR g.name LIKE ?
    """
    params = [f"%{query_text}%", f"%{query_text}%", f"%{query_text}%"]

    if query_text.isdigit():
        sql += " OR a.year = ?"
        params.append(int(query_text))
    return [dict(row) for row in query(sql, params)]

def get_all_albums(user_id=None):
    """
    Fetches all albums, optionally filtering by user.
    """
    sql = """
        SELECT DISTINCT a.id, a.title, a.artist, a.year, a.image_url, u.username AS owner_username
        FROM albums a
        JOIN users u ON a.user_id = u.id
        LEFT JOIN album_genres ag ON a.id = ag.album_id
    """
    rows = query(sql)
    albums = [dict(row) for row in rows]
    for album in albums:
        album['genres'] = get_album_genres(album['id'])
    return albums

def get_user_favorites(user_id):
    """
    Fetches favorite albums for a specific user.
    """
    sql = """
        SELECT a.id, a.title, a.artist, a.year, a.image_url,
               (SELECT 1 FROM favorites f WHERE f.album_id = a.id AND f.user_id = ?) AS is_favorite
        FROM albums a
        JOIN favorites f2 ON a.id = f2.album_id
        WHERE f2.user_id = ?
    """
    rows = query(sql, (user_id, user_id))
    albums = [dict(row) for row in rows]
    for album in albums:
        album['genres'] = get_album_genres(album['id'])
    return albums

def get_user_albums(user_id):
    """
    Fetches albums added by a specific user.
    """
    sql = """
        SELECT DISTINCT a.id, a.title, a.artist, a.year, a.image_url,
               u.username AS owner_username
        FROM albums a
        JOIN users u ON a.user_id = u.id
        LEFT JOIN album_genres ag ON a.id = ag.album_id
        WHERE a.user_id = ?
    """
    rows = query(sql, (user_id,))
    albums = [dict(row) for row in rows]
    for album in albums:
        album['genres'] = get_album_genres(album['id'])
    return albums

def get_user_stats(user_id):
    """Get statistics for a user: num albums, total reviews, avg album rating."""
    stats = {}
    stats['num_albums'] = query(
        "SELECT COUNT(id) as count FROM albums WHERE user_id = ?",
        (user_id,)
    )[0]['count']
    stats['total_reviews'] = query("""
        SELECT COUNT(r.id) as count
        FROM reviews r
        JOIN albums a ON r.album_id = a.id
        WHERE a.user_id = ?
    """, (user_id,))[0]['count']
    avg_rating = query("""
        SELECT AVG(r.stars) as avg
        FROM reviews r
        JOIN albums a ON r.album_id = a.id
        WHERE a.user_id = ?
    """, (user_id,))
    stats['avg_album_rating'] = (
        round(avg_rating[0]['avg'], 1) if avg_rating[0]['avg'] else 0
    )
    return stats
