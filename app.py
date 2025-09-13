from flask import Flask, render_template, request, redirect, session
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
        return redirect("/login")
    return render_template("add.html")

@app.route("/result", methods=["POST"])
def result():
    title = request.form["title"]
    artist = request.form["artist"]
    year = request.form["year"]
    genre = request.form["genre"]
    db.execute("INSERT INTO albums (title, artist, year, genre) VALUES (?, ?, ?, ?)", (title, artist, year, genre))
    return render_template("result.html", title=title, artist=artist, year=year, genre=genre)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "error: Passwords don't match"
    password_hash = generate_password_hash(password1)

    try:
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
    except sqlite3.IntegrityError:
        return "error: Username taken"

    return redirect("/")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/insert", methods=["POST"])
def insert():
    username = request.form["username"]
    password = request.form["password"]

    result = db.query("SELECT password_hash FROM users WHERE username = ?", (username,))
    if not result:
        return "error: Wrong username or password"
    password_hash = result[0]["password_hash"]

    if check_password_hash(password_hash, password):
        session["username"] = username
        return redirect("/")
    else:
        return "error: Wrong username or password"

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")
