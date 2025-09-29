from db import query, execute

def add_album(title, artist, year, genre, user_id, image_url=None):
    try:
        execute(
            "INSERT INTO albums (title, artist, year, genre, user_id, image_url) VALUES (?, ?, ?, ?, ?, ?)",
            (title, artist, year, genre, user_id, image_url)
        )
        return True, "Album added successfully."
    except Exception as e:
        return False, str(e)

def update_album(album_id, title, artist, year, genre, image_url):
    execute("""
        UPDATE albums SET title = ?, artist = ?, year = ?, genre = ?, image_url = ?
        WHERE id = ?
    """, (title, artist, year, genre, image_url, album_id))

def delete_album(album_id):
    execute("DELETE FROM albums WHERE id = ?", (album_id,))


def validate_album_data(data):
    errors = {}
    if not data.get("title"):
        errors["title"] = "Title is required."
    if not data.get("artist"):
        errors["artist"] = "Artist is required."
    if not data.get("year") or not data["year"].isdigit():
        errors["year"] = "Year must be a number."
    if not data.get("genre"):
        errors["genre"] = "Genre is required."
    return errors

def search_albums(query_text, user_id=None):
    sql = """
        SELECT a.*, u.username AS owner_username
        FROM albums a
        JOIN users u ON a.user_id = u.id
        WHERE a.title LIKE ? OR a.artist LIKE ? OR a.genre LIKE ?
    """
    params = [f"%{query_text}%", f"%{query_text}%", f"%{query_text}%"]

    if query_text.isdigit():
        sql += " OR a.year = ?"
        params.append(int(query_text))
    return [dict(row) for row in query(sql, params)]

def get_all_albums(user_id=None):
    sql = """
        SELECT a.*, u.username AS owner_username
        FROM albums a
        JOIN users u ON a.user_id = u.id
    """
    return [dict(row) for row in query(sql)]

def get_user_favorites(user_id):
    rows = query("""
        SELECT a.*,
               (SELECT 1 FROM favorites f WHERE f.album_id = a.id AND f.user_id = ?) AS is_favorite
        FROM albums a
        JOIN favorites f2 ON a.id = f2.album_id
        WHERE f2.user_id = ?
    """, (user_id, user_id))
    return [dict(row) for row in rows]

def get_album_reviews(album_id):
    from db import query
    sql = "SELECT r.*, u.username FROM reviews r JOIN users u ON r.user_id = u.id WHERE r.album_id = ? ORDER BY r.id DESC"
    return [dict(row) for row in query(sql, (album_id,))]

def get_album_avg_rating(album_id):
    sql = "SELECT AVG(stars) as avg_stars FROM reviews WHERE album_id = ?"
    result = query(sql, (album_id,))
    return result[0]["avg_stars"] if result and result[0]["avg_stars"] is not None else 0

def has_user_reviewed(album_id, user_id):
    sql = "SELECT 1 FROM reviews WHERE album_id = ? AND user_id = ?"
    result = query(sql, (album_id, user_id))
    return bool(result)

def get_album_by_id(album_id):
    rows = query("""
        SELECT a.*, u.username AS owner_username
        FROM albums a
        JOIN users u ON a.user_id = u.id
        WHERE a.id = ?
    """, (album_id,))
    return dict(rows[0]) if rows else None
