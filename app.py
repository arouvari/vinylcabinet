from flask import Flask, render_template, request, redirect, session, flash, get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/", methods=["GET"])
def index():
    query = request.args.get("query", "").strip()
    user_id = session.get("user_id")

    if query:
        if user_id:
            albums = db.query("""
                SELECT a.id, a.title, a.artist, a.year, a.genre, a.user_id, a.image_url,
                EXISTS (SELECT 1 FROM favorites f
                WHERE f.user_id = ? AND f.album_id = a.id),
                AS is_favorite,
                (SELECT AVG(r.stars) FROM reviews r WHERE r.album_id = a.id) AS avg_stars
                FROM albums a
                WHERE a.title LIKE ? OR a.artist LIKE ? OR a.year LIKE ? OR a.genre LIKE ?
            """, (user_id, f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
        else:
            albums = db.query("""
                SELECT id, title, artist, year, genre, user_id, image_url,
                (SELECT AVG(r.stars) FROM reviews r WHERE r.album_id = albums.id) as avg_stars
                FROM albums
                WHERE title LIKE ? OR artist LIKE ? OR year LIKE ? OR genre LIKE ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
    else:
        if user_id:
            albums = db.query("""
                            SELECT a.id, a.title, a.artist, a.year, a.genre, a.user_id, a.image_url,
                            EXISTS (SELECT 1 FROM favorites f
                            WHERE f.user_id = ? AND f.album_id = a.id)
                            AS is_favorite,
                            (SELECT AVG(r.stars) FROM reviews r WHERE r.album_id = a.id)
                            AS avg_stars
                            FROM albums a""", (user_id,))
        else:
            albums = db.query("""SELECT id, title, artist, year, genre, user_id, image_url,
                                (SELECT AVG(r.stars) FROM reviews r WHERE r.album_id = albums.id)
                                AS avg_stars
                                FROM albums
                              """)
    return render_template("index.html", albums=albums, query=query)

@app.route("/add")
def add():
    if "username" not in session:
        flash("You must be logged in to add albums", "error")
        return redirect("/login")
    return render_template("add.html")

@app.route("/result", methods=["POST"])
def result():
    if "username" not in session:
        return redirect("/login")

    title = request.form["title"]
    artist = request.form["artist"]
    year = request.form["year"]
    genre = request.form["genre"]
    user_id=session["user_id"]
    image_url = request.form.get("image_url")

    if not title or not artist:
        flash("Title and artist are required", "error")
        return redirect("/add")
    if year and not year.isdigit():
        flash("Year must be a number", "error")
        return redirect("/add")

    db.execute("INSERT INTO albums (title, artist, year, genre, user_id, image_url) VALUES (?, ?, ?, ?, ?, ?)", (title, artist, year, genre, user_id, image_url))
    flash(f"Album '{title}' added!", "success")
    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_post():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        flash("Passwords don't match", "error")
        return redirect("/register")
    password_hash = generate_password_hash(password1)

    try:
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
    except sqlite3.IntegrityError:
        flash("Username taken", "error")
        return redirect("/register")

    flash("Account registered", "success")
    return redirect("/login")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    username = request.form["username"]
    password = request.form["password"]

    result = db.query("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    if not result:
        flash("Wrong username or password", "error")
        return redirect("/login")
    user_id = result[0]["id"]
    password_hash = result[0]["password_hash"]

    if check_password_hash(password_hash, password):
        session["username"] = username
        session["user_id"] = user_id
        flash("Logged in successfully", "success")
        return redirect("/")
    else:
        flash("Wrong username or password", "error")
        return redirect("/login")

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("user_id", None)
    flash("Logged out successfully", "success")
    return redirect("/")

@app.route("/delete/<int:album_id>", methods=["POST"])
def delete_album(album_id):
    if "username" not in session:
        flash("You must be logged in to delete albums", "error")
        return redirect("/login")

    album = db.query("SELECT user_id FROM albums WHERE id = ?", (album_id,))
    if not album:
        flash("Album not found", "error")
        return redirect("/")
    if album[0]["user_id"] != session["user_id"]:
        flash("You are not allowed to delete this album", "error")
        return redirect("/")

    db.execute("DELETE FROM albums WHERE id = ?", (album_id,))
    flash("Album deleted successfully", "success")
    return redirect("/")

@app.route("/edit/<int:album_id>")
def edit_album(album_id):
    if "username" not in session:
        flash("You must be logged in to edit albums", "error")
        return redirect("/login")

    album = db.query("SELECT * FROM albums WHERE id = ?", (album_id,))
    if not album:
        flash("Album not found", "error")
        return redirect("/")

    album = album[0]
    if album["user_id"] != session["user_id"]:
        flash("You cannot edit this album", "error")
        return redirect("/")

    return render_template("edit.html", album=album)

@app.route("/edit/<int:album_id>", methods=["POST"])
def edit_album_post(album_id):
    if "username" not in session:
        flash("You must be logged in to edit albums", "error")
        return redirect("/login")

    title = request.form["title"]
    artist = request.form["artist"]
    year = request.form["year"]
    genre = request.form["genre"]
    image_url = request.form["image_url"]

    if not title or not artist:
        flash("Title and artist are required", "error")
        return redirect(f"/edit/{album_id}")
    if year and not year.isdigit():
        flash("Year must be a number", "error")
        return redirect(f"/edit/{album_id}")

    db.execute("UPDATE albums SET title = ?, artist = ?, year = ?, genre = ?, image_url = ? WHERE id = ?",
               (title, artist, year, genre, image_url, album_id))
    flash("Album updated successfully", "success")
    return redirect("/")

@app.route("/favorite/<int:album_id>", methods=["POST"])
def favorite(album_id):
    if "user_id" not in session:
        flash("You must be logged in to favorite albums", "error")
        return redirect("/login")

    user_id = session["user_id"]

    existing = db.query("SELECT 1 FROM favorites WHERE user_id = ? AND album_id = ?", (user_id, album_id))
    if existing:
        db.execute("DELETE FROM favorites WHERE user_id = ? AND album_id = ?", (user_id, album_id))
        flash("Album removed from favorites", "success")
    else:
        db.execute("INSERT INTO favorites (user_id, album_id) VALUES (?, ?)", (user_id, album_id))
        flash("Album added to favorites", "success")

    return redirect("/")

@app.route("/user/<username>")
def user_page(username):
    user = db.query("SELECT id FROM users WHERE username = ?", (username,))
    if not user:
        flash("User not found", "error")
        return redirect("/")
    profile_user_id = user[0]["id"]

    albums = db.query("""
        SELECT a.id, a.title, a.artist, a.year, a.genre, a.user_id, a.image_url
        FROM albums a
        JOIN favorites f ON a.id = f.album_id
        WHERE f.user_id = ?
                      """, (profile_user_id,))

    current_user_id = session.get("user_id")
    user_favorites = []
    if current_user_id:
        favorites = db.query("SELECT album_id FROM favorites WHERE user_id = ?", (current_user_id,))
        user_favorites = [f["album_id"] for f in favorites]

    return render_template("user.html", albums=albums, username=username, user_favorites=user_favorites)

@app.route("/album/<int:album_id>")
def album_detail(album_id):
    album = db.query("SELECT * FROM albums WHERE id = ?", (album_id,))
    if not album:
        flash("Album not found", "error")
        return redirect("/")
    album = album[0]

    user_id = session.get("user_id")
    reviews = db.query("""
                        SELECT r.stars, r.text, r.created_at, u.username
                       FROM reviews r
                       JOIN users u ON r.user_id = u.id
                       WHERE r.album_id = ?
                       ORDER BY r.created_at DESC
                       """, (album_id,))

    avg_stars = db.query("SELECT AVG(stars) AS avg FROM reviews WHERE album_id = ?", (album_id,))[0]["avg"] or 0
    has_reviewed = False
    if user_id:
        has_reviewed = bool(db.query("SELECT 1 FROM reviews WHERE album_id = ? AND user_id = ?", (album_id, user_id)))

    return render_template("album.html", album=album, reviews=reviews, avg_stars=avg_stars, has_reviewed=has_reviewed)

@app.route("/review/<int:album_id>", methods=["POST"])
def add_review(album_id):
    if "user_id" not in session:
        flash("You must be logged in to add reviews", "error")
        return redirect

    stars = request.form.get("stars")
    text = request.form.get("text", "").strip()

    if not stars or not stars.isdigit() or int(stars) < 1 or int(stars) > 5:
        flash("Stars must be between 1 and 5", "error")
        return redirect(f"/album{album_id}")

    try:
        db.execute("INSERT INTO reviews (album_id, user_id, stars, text) VALUES (?, ?, ?, ?)",
                   (album_id, session["user_id"], stars, text))
        flash("Review added!", "success")
    except sqlite3.IntegrityError:
        flash("You have already reviewed this album", "error")

    return redirect(f"/album/{album_id}")
