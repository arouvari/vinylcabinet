import db
from models import Vinyl

def get_all_vinyls():
    try:
        return Vinyl.query.all()
    except Exception as e:
        print(f"Database error: {e}")
        return []

def add_vinyl(album, artist, year, genre=None):
    try:
        vinyl = Vinyl(album=album, artist=artist, year=year, genre=genre)
        db.session.add(vinyl)
        db.session.commit()
        return True, "Vinyl added successfully"
    except Exception as e:
        db.session.rollback()
        return False, f"Error adding vinyl: {str(e)}"

def search_vinyls(query):
    try:
        if not query:
            return get_all_vinyls()

        return Vinyl.query.filter(
            db.or_(
                Vinyl.album.ilike(f"%{query}%"),
                Vinyl.artist.ilike(f"%{query}%"),
                Vinyl.genre.ilike(f"%{query}%")
            )
        ).all()
    except Exception as e:
        print(f"Search error: {e}")
        return []

def validate_vinyl_data(form_data):
    errors = {}

    album = form_data.get("album", "").strip()
    if not album:
        errors["album"] = "Album name is required"
    elif len(album) > 100:
        errors["album"] = "Album name must be less than 100 characters"

    artist = form_data.get("artist", "").strip()
    if not artist:
        errors["artist"] = "Artist is required"
    elif len(artist) > 100:
        errors["artist"] = "Artist must be less than 100 characters"

    year_str = form_data.get("year", "").strip()
    if not year_str:
        errors["year"] = "Year is required"
    else:
        try:
            year = int(year_str)
            if year < 1900 or year > 2024:
                errors["year"] = "Year must be between 1900 and 2024"
        except ValueError:
            errors["year"] = "Year must be a number"

    genre = form_data.get("genre", "").strip()
    if genre and len(genre) > 50:
        errors["genre"] = "Genre must be less than 50 characters"

    return errors