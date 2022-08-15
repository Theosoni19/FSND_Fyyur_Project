from flask import Flask
from sqlalchemy import ARRAY, String
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object("config")
db = SQLAlchemy(app)       # Instance of database
migrate = Migrate(app, db) # database migration

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Shows(db.Model):
    __tablename__ = "shows"
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist = db.relationship("Artist", backref="shows", lazy=True)
    venue = db.relationship("Venue", backref="shows", lazy=True)

class Artist(db.Model):
    __tablename__ = "artists"
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String,unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(String), nullable=False)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String)

class Venue(db.Model):
    __tablename__ = "venues"
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String,unique=True, nullable=False) 
    city = db.Column(db.String(120), nullable=False) 
    state = db.Column(db.String(120), nullable=False) 
    address = db.Column(db.String(120), nullable=False) 
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(String), nullable=False) 
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String)