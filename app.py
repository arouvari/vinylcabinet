from flask import Flask, render_template, request, redirect
from werkzeug.security import generate_password_hash
import sqlite3
import db

app = Flask(__name__)

@app.route("/")
def index():
    albums = db.query("SELECT title, artist, year, genre FROM albums")
    return render_template("index.html", albums=albums)

@app.route("/add")
def add():
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
