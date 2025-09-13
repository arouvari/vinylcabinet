from flask import Flask, render_template, request, redirect
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
    db.query("INSERT INTO albums (title, artist, year, genre) VALUES (?, ?, ?, ?)", (title, artist, year, genre))
    return render_template("result.html", title=title, artist=artist, year=year, genre=genre)
