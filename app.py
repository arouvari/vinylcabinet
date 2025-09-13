from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add")
def add():
    return render_template("add.html")

@app.route("/result", methods=["POST"])
def result():
    title = request.form["title"]
    artist = request.form["artist"]
    genre = request.form["genre"]
    return render_template("result.html", title=title, artist=artist, genre=genre)
