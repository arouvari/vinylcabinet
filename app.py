from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import config
import db
import database

app = Flask(__name__)
app.secret_key = config.secret_key

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

@app.route("/", methods=["GET"])
def index():
    query = request.args.get("query", "").strip()
    user_id = session.get("user_id")

    if query:
        albums = database.search_albums(query, user_id)
    else:
        albums = database.get_all_albums(user_id)

    albums = [dict(album) for album in albums]

    return render_template("index.html", albums=albums, query=query)

@app.route("/add", methods=["GET", "POST"])
def add():
    if "username" not in session:
        flash("You must be logged in to add albums", "error")
        return redirect("/login")

    form_data = {}
    if request.method == "POST":
        form_data = {
            "title": request.form.get("title", "").strip(),
            "artist": request.form.get("artist", "").strip(),
            "year": request.form.get("year", "").strip(),
            "genre": request.form.get("genre", "").strip(),
            "image_url": request.form.get("image_url", "").strip()
        }

        errors = database.validate_album_data(form_data)

        if errors:
            return render_template(
                "album_form.html",
                page_title="Add Vinyl",
                submit_label="Add",
                errors=errors,
                form_data=form_data,
                album=None
            )

        success, message = database.add_album(
            form_data["title"],
            form_data["artist"],
            int(form_data["year"]),
            form_data["genre"],
            session["user_id"],
            form_data["image_url"] or None
        )

        if success:
            flash(message, "success")
            return redirect("/")
        else:
            flash(message, "error")
            return render_template(
                "album_form.html",
                page_title="Add Vinyl",
                submit_label="Add",
                form_data=form_data,
                album=None
            )

    return render_template(
        "album_form.html",
        page_title="Add Vinyl",
        submit_label="Add",
        album=None
    )


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

@app.route("/edit/<int:album_id>", methods=["GET", "POST"])
def edit_album(album_id):
    if "username" not in session:
        flash("You must be logged in to edit albums", "error")
        return redirect("/login")

    album = database.get_album_by_id(album_id)
    if not album:
        flash("Album not found", "error")
        return redirect("/")

    if album["user_id"] != session["user_id"]:
        flash("You cannot edit this album", "error")
        return redirect("/")

    form_data = {}
    if request.method == "POST":
        form_data = {
            "title": request.form.get("title", "").strip(),
            "artist": request.form.get("artist", "").strip(),
            "year": request.form.get("year", "").strip(),
            "genre": request.form.get("genre", "").strip(),
            "image_url": request.form.get("image_url", "").strip()
        }

        errors = database.validate_album_data(form_data)

        if errors:
            return render_template(
                "album_form.html",
                page_title="Edit Vinyl",
                submit_label="Update",
                errors=errors,
                form_data=form_data,
                album=None
            )

        database.update_album(
            album_id,
            form_data["title"],
            form_data["artist"],
            int(form_data["year"]),
            form_data["genre"],
            form_data["image_url"] or None
        )

        flash("Album updated successfully", "success")
        return redirect("/")

    return render_template(
        "album_form.html",
        page_title="Edit Vinyl",
        submit_label="Update",
        album=album
    )


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
    albums = database.get_user_favorites(profile_user_id)

    current_user_id = session.get("user_id")
    user_favorites = []
    if current_user_id:
        favorites = db.query("SELECT album_id FROM favorites WHERE user_id = ?", (current_user_id,))
        user_favorites = [f["album_id"] for f in favorites]

    return render_template("user.html", albums=albums, username=username, user_favorites=user_favorites)

@app.route("/album/<int:album_id>")
def album_detail(album_id):
    album = database.get_album_by_id(album_id)
    if not album:
        flash("Album not found", "error")
        return redirect("/")

    reviews = database.get_album_reviews(album_id)
    avg_stars = database.get_album_avg_rating(album_id)

    user_id = session.get("user_id")
    has_reviewed = database.has_user_reviewed(album_id, user_id) if user_id else False

    return render_template("album.html", album=album, reviews=reviews, avg_stars=avg_stars, has_reviewed=has_reviewed)

@app.route("/review/<int:album_id>", methods=["POST"])
def add_review(album_id):
    if "user_id" not in session:
        flash("You must be logged in to add reviews", "error")
        return redirect("/login")

    stars = request.form.get("stars")
    text = request.form.get("text", "").strip()

    if not stars or not stars.isdigit() or int(stars) < 1 or int(stars) > 5:
        flash("Stars must be between 1 and 5", "error")
        return redirect(f"/album/{album_id}")

    try:
        db.execute("INSERT INTO reviews (album_id, user_id, stars, text) VALUES (?, ?, ?, ?)",
                   (album_id, session["user_id"], stars, text))
        flash("Review added!", "success")
    except sqlite3.IntegrityError:
        flash("You have already reviewed this album", "error")

    return redirect(f"/album/{album_id}")

if __name__ == "__main__":
    app.run(debug=True)