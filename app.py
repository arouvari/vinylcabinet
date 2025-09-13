from flask import Flask, render_template, request, redirect, session, flash, get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    albums = db.query("SELECT title, artist, year, genre FROM albums")
    return render_template("index.html", albums=albums)

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

    if not title or not artist:
        flash("Title and artist are required", "error")
        return redirect("/add")
    if year and not year.isdigit():
        flash("Year must be a number", "error")
        return redirect("/add")

    db.execute("INSERT INTO albums (title, artist, year, genre, user_id) VALUES (?, ?, ?, ?, ?)", (title, artist, year, genre, user_id))
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
