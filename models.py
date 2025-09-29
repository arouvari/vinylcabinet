from app import db

class Vinyl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    album = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(50))

    def __repr__(self):
        return f"<Vinyl {self.album} by {self.artist}>"