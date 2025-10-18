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
    search_terms = query_text.split()

    if not search_terms:
        return []

    conditions = []
    params = []

    for term in search_terms:
        term_pattern = f"%{term}%"
        conditions.append(
            "(a.title LIKE ? OR a.artist LIKE ? OR g.name LIKE ? "
            "OR CAST(a.year AS TEXT) LIKE ?)"
        )
        params.extend([term_pattern, term_pattern, term_pattern, term_pattern])

    where_clause = " AND ".join(conditions)

    sql = f"""
        SELECT DISTINCT a.id, a.title, a.artist, a.year, a.image_url, a.user_id,
               u.username AS owner_username
        FROM albums a
        JOIN users u ON a.user_id = u.id
        LEFT JOIN album_genres ag ON a.id = ag.album_id
        LEFT JOIN genres g ON ag.genre_id = g.id
        WHERE {where_clause}
    """

    rows = query(sql, params)
    albums = [dict(row) for row in rows]
    for album in albums:
        album['genres'] = get_album_genres(album['id'])
    return albums

def get_all_albums(user_id=None):
    """
    Fetches all albums, optionally filtering by user.
    """
    sql = """
        SELECT DISTINCT a.id, a.title, a.artist, a.year, a.image_url, a.user_id,
               u.username AS owner_username
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
def get_album_by_id(album_id):
    """
    Fetches a single album by its ID.
    """
    sql = """
        SELECT a.id, a.title, a.artist, a.year, a.image_url, a.user_id,
               u.username AS owner_username
        FROM albums a
        JOIN users u ON a.user_id = u.id
        WHERE a.id = ?
    """
    rows = query(sql, (album_id,))
    if not rows:
        return None
    album = dict(rows[0])
    album['genres'] = get_album_genres(album_id)
    return album

def get_album_reviews(album_id):
    """
    Fetches all reviews for a specific album.
    """
    sql = """
        SELECT r.id, r.stars, r.text, r.created_at, u.username
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.album_id = ?
        ORDER BY r.created_at DESC
    """
    rows = query(sql, (album_id,))
    return [dict(row) for row in rows]

def get_album_avg_rating(album_id):
    """
    Calculates the average rating for an album.
    """
    sql = "SELECT AVG(stars) as avg FROM reviews WHERE album_id = ?"
    result = query(sql, (album_id,))
    avg = result[0]['avg'] if result and result[0]['avg'] else None
    return round(avg, 1) if avg else None

def has_user_reviewed(album_id, user_id):
    """
    Checks if a user has already reviewed an album.
    """
    if not user_id:
        return False
    sql = "SELECT 1 FROM reviews WHERE album_id = ? AND user_id = ?"
    result = query(sql, (album_id, user_id))
    return bool(result)

def get_user_profile(user_id):
    """
    Fetches user profile information.
    """
    sql = """
        SELECT u.id, u.username, up.bio, up.location, up.profile_image_url,
               up.joined_date, up.favorite_genre_id, g.name as favorite_genre
        FROM users u
        LEFT JOIN user_profiles up ON u.id = up.user_id
        LEFT JOIN genres g ON up.favorite_genre_id = g.id
        WHERE u.id = ?
    """
    rows = query(sql, (user_id,))
    return dict(rows[0]) if rows else None

def update_user_profile(user_id, bio, location, profile_image_url, favorite_genre_id):
    """
    Updates or creates a user profile.
    """
    existing = query("SELECT user_id FROM user_profiles WHERE user_id = ?", (user_id,))

    if existing:
        execute("""
            UPDATE user_profiles
            SET bio = ?, location = ?, profile_image_url = ?, favorite_genre_id = ?
            WHERE user_id = ?
        """, (bio, location, profile_image_url, favorite_genre_id, user_id))
    else:
        execute("""
            INSERT INTO user_profiles (user_id, bio, location, profile_image_url, favorite_genre_id)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, bio, location, profile_image_url, favorite_genre_id))

def get_user_activity(user_id):
    """
    Fetches recent user activity.
    """
    recent_albums = query("""
        SELECT id, title, artist
        FROM albums
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 5
    """, (user_id,))

    recent_reviews = query("""
        SELECT r.id, r.stars, r.text, r.created_at, a.title as album_title, a.id as album_id
        FROM reviews r
        JOIN albums a ON r.album_id = a.id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
        LIMIT 5
    """, (user_id,))

    return {
        'recent_albums': [dict(row) for row in recent_albums],
        'recent_reviews': [dict(row) for row in recent_reviews]
    }
