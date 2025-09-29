from flask import render_template, request, redirect, url_for, flash
import app
from database import get_all_vinyls, add_vinyl, search_vinyls, validate_vinyl_data

@app.route("/")
def index():
    search_query = request.args.get("q", "")
    if search_query:
        vinyls = search_vinyls(search_query)
    else:
        vinyls = get_all_vinyls()
    return render_template("index.html", vinyls=vinyls, search_query=search_query)

@app.route("/add", methods=["GET", "POST"])
def add_vinyl_route():
    errors = {}
    form_data = {}

    if request.method == "POST":
        form_data = {
            "album": request.form.get("album", ""),
            "artist": request.form.get("artist", ""),
            "year": request.form.get("year", ""),
            "genre": request.form.get("genre", "")
        }
        errors = validate_vinyl_data(form_data)

        if not errors:
            success, message = add_vinyl(
                form_data["album"],
                form_data["artist"],
                int(form_data["year"]),
                form_data["genre"]
            )

            if success:
                flash(message, "success")
                return redirect(url_for("index"))
            else:
                flash(message, "error")
        else:
            flash("Please correct the errors below", "error")

    return render_template("add_vinyl.html", errors=errors, form_data=form_data)

@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html"), 500