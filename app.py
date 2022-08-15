#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------

import itertools
import dateutil.parser
import babel
from flask import render_template, request, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
from model import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
        date = dateutil.parser.parse(value)
  else:
        date = value

  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route("/")
def index():
  return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------

@app.route("/venues")
def venues():
  # Show all venues from db
  data = []
  sortedData = {"city":"",
                "state":"",
                "venues":[]
                }
  allVenues = Venue.query.all()
  # To sort and group the venues data by their city and state
  sort_function = lambda d: (d.city,d.state)
  # see https://docs.python.org/3/library/functions.html?highlight=sorted#sorted
  sortedVenues = sorted(allVenues, key=sort_function)          
  # see https://docs.python.org/3/library/itertools.html    
  groupOfVenues = itertools.groupby(sortedVenues, key=sort_function)

  for key, venue in groupOfVenues:
    
    sortedData["city"] = key[0]
    sortedData["state"] = key[1]
    
    for v in list(venue):
      # filter the start_time of venue's shows
      upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(),v.shows)) 
      datas={
        "id":v.id,
        "name":v.name,
        "num_upcoming_shows": len(upcoming_shows)
      }
      sortedData["venues"].append(datas)
      datas={}
    data.append(sortedData)
    sortedData={"city":"",
                "state":"",
                "venues":[]}

  return render_template("pages/venues.html", areas = data)

@app.route("/venues/search", methods=["POST"])
def search_venues():
  # Implementation of search on venues with partial string search (case-insensitive)

  search_term=request.form.get("search_term", "")
  venues = Venue.query.filter(Venue.name.ilike("%"+search_term+"%")).all()
  
  response = {
      "count": 0,
      "data": []
    }
  for venue in venues:
        upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(),venue.shows))
        response["count"] += 1
        response["data"].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(upcoming_shows)
        })

  return render_template("pages/search_venues.html", results=response, search_term=request.form.get("search_term", ""))

@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
  # show the artist page with the given venue_id

  data = {}
  show = {}
  past_shows = []
  upcoming_shows = []
  venue = Venue.query.get(venue_id)

  all_past_shows = list(filter(lambda show: show.start_time < datetime.now(),venue.shows))
  all_upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(),venue.shows))

  for datas in all_past_shows:
    show["artist_id"] = datas.artist.id
    show["artist_name"] = datas.artist.name
    show["artist_image_link"] = datas.artist.image_link
    show["start_time"] = datas.start_time
    past_shows.append(show)
    show = {} 
  
  for datas in all_upcoming_shows:
    show["artist_id"] = datas.artist.id
    show["artist_name"] = datas.artist.name
    show["artist_image_link"] = datas.artist.image_link
    show["start_time"] = datas.start_time
    upcoming_shows.append(show)
    show = {} 

  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)
  
  data["id"] = venue.id
  data["name"] = venue.name
  data["genres"] = venue.genres
  data["address"] = venue.address
  data["city"] = venue.city
  data["state"] = venue.state
  data["phone"] = venue.phone
  data["website"] = venue.website
  data["facebook_link"] = venue.facebook_link
  data["seeking_talent"] = venue.seeking_talent
  data["seeking_description"] = venue.seeking_description
  data["image_link"] = venue.image_link
  data["past_shows"] = past_shows
  data["upcoming_shows"] = upcoming_shows
  data["past_shows_count"] = past_shows_count
  data["upcoming_shows_count"] = upcoming_shows_count
 
  return render_template("pages/show_venue.html", venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route("/venues/create", methods=["GET"])
def create_venue_form():
  # Create a venue form in the frontend
  form = VenueForm()
  return render_template("forms/new_venue.html", form=form)

@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
  # insertion of form data as a new Venue record in the db

  form = VenueForm()
  if form.validate_on_submit():
    try:
          venue = Venue(name = form.name.data,
                          city = form.city.data,
                          state = form.state.data,
                          address = form.address.data,
                          phone = form.phone.data,
                          image_link = form.image_link.data,
                          genres = form.genres.data,
                          facebook_link = form.facebook_link.data,
                          website = form.website_link.data,
                          seeking_talent = form.seeking_talent.data,
                          seeking_description = form.seeking_description.data)
          db.session.add(venue)
          db.session.commit()
          # Flash on successful db insert | see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
          flash("Venue " + venue.name + " was successfully listed!")
          db.session.close()
          return render_template("pages/home.html")
    except:
          db.session.rollback()
          db.session.close()
          flash("An error occurred. Venue " + request.form.get("name") + " could not be listed.")
          return render_template("forms/new_venue.html", form=form)

  else: 
      flash(form.errors)
      return render_template("forms/new_venue.html", form=form)


@app.route("/venues/<venue_id>/delete" ,methods=["DELETE"])
def delete_venue(venue_id):
  # Delete a record in db
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    db.session.close()
  except:
    db.session.rollback()
    db.session.close()
  finally:
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
  # Show all artists from db
  artists = Artist.query.order_by(Artist.id).all()
  eachArtist={}
  data=[]
  for artist in artists:
    eachArtist["id"] = artist.id
    eachArtist["name"] = artist.name
    data.append(eachArtist)
    eachArtist={}

  return render_template("pages/artists.html", artists=data)

@app.route("/artists/search", methods=["POST"])
def search_artists():
  # implementation of search on artists with partial string search (case-insensitive)

  search_term=request.form.get("search_term", "")
  artists = Artist.query.filter(Artist.name.ilike("%"+search_term+"%")).all()
  
  response = {
      "count": 0,
      "data": []
    }

  for artist in artists:
        upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(),artist.shows))
        response["count"] += 1
        response["data"].append({
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": len(upcoming_shows)
        })

  return render_template("pages/search_artists.html", results=response, search_term=request.form.get("search_term", ""))

@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
  # shows the artist page with the given artist_id

  data = {}
  show = {}
  past_shows = []
  upcoming_shows = []
  artist = Artist.query.get(artist_id)

  all_past_shows = list(filter(lambda show: show.start_time < datetime.now(),artist.shows))
  all_upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(),artist.shows))

  for datas in all_past_shows:
    show["venue_id"] = datas.venue.id
    show["venue_name"] = datas.venue.name
    show["venue_image_link"] = datas.venue.image_link
    show["start_time"] = datas.start_time
    past_shows.append(show)
    show = {} 
  
  for datas in all_upcoming_shows:
    show["venue_id"] = datas.venue.id
    show["venue_name"] = datas.venue.name
    show["venue_image_link"] = datas.venue.image_link
    show["start_time"] = datas.start_time
    upcoming_shows.append(show)
    show = {} 

  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)
  
  data["id"] = artist.id
  data["name"] = artist.name
  data["genres"] = artist.genres
  data["city"] = artist.city
  data["state"] = artist.state
  data["phone"] = artist.phone
  data["website"] = artist.website
  data["facebook_link"] = artist.facebook_link
  data["seeking_venue"] = artist.seeking_venue
  data["seeking_description"] = artist.seeking_description
  data["image_link"] = artist.image_link
  data["past_shows"] = past_shows
  data["upcoming_shows"] = upcoming_shows
  data["past_shows_count"] = past_shows_count
  data["upcoming_shows_count"] = upcoming_shows_count
  
  return render_template("pages/show_artist.html", artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
  # populate form with fields from artist with ID <artist_id>

  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template("forms/edit_artist.html", form=form, artist=artist)

@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
  # updating existing artist record with ID <artist_id> using the new attributes
  
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  artist.name = form.name.data
  artist.genres = form.genres.data
  artist.city = form.city.data
  artist.state = form.state.data
  artist.phone = form.phone.data
  artist.website = form.website_link.data
  artist.facebook_link = form.facebook_link.data
  artist.seeking_venue = form.seeking_venue.data
  artist.seeking_description = form.seeking_description.data
  artist.image_link = form.image_link.data
  db.session.commit()

  return redirect(url_for("show_artist", artist_id=artist_id))

@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
  # populate form with fields from venue with ID <venue_id>
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template("forms/edit_venue.html", form=form, venue=venue)

@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
  # updating existing venue record with ID <venue_id> using the new attributes

  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue.name = form.name.data
  venue.genres = form.genres.data
  venue.address = form.address.data
  venue.city = form.city.data
  venue.state = form.state.data
  venue.phone = form.phone.data
  venue.website = form.website_link.data
  venue.facebook_link = form.facebook_link.data
  venue.seeking_talent = form.seeking_talent.data
  venue.seeking_description = form.seeking_description.data
  venue.image_link = form.image_link.data
  db.session.commit()

  return redirect(url_for("show_venue", venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route("/artists/create", methods=["GET"])
def create_artist_form():
  # Create a artist form in the frontend

  form = ArtistForm()
  return render_template("forms/new_artist.html", form=form)

@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
   # insertion of form data as a new Venue record in the db

  form = ArtistForm()
  if form.validate_on_submit():
      try:
          artist = Artist(name = form.name.data,
                          city = form.city.data,
                          state = form.state.data,
                          phone = form.phone.data,
                          image_link = form.image_link.data,
                          genres = form.genres.data,
                          facebook_link = form.facebook_link.data,
                          website = form.website_link.data,
                          seeking_venue = form.seeking_venue.data,
                          seeking_description = form.seeking_description.data)
          db.session.add(artist)
          db.session.commit()
          # on successful db insert, flash success
          flash("Artist " + artist.name + " was successfully listed!")
          db.session.close()
          return render_template("pages/home.html")
  
  # on unsuccessful db insert, flash an error instead.
      except:
          db.session.rollback()
          db.session.close()
          flash("An error occurred. Artist " + request.form.get("name") + " could not be listed.")
          return render_template("forms/new_artist.html", form=form)

  else: 
      flash(form.errors)
      return render_template("forms/new_artist.html", form=form)
  


#  Shows
#  ----------------------------------------------------------------

@app.route("/shows")
def shows():
  # displays list of shows

    data = []
    show = {}
    shows = Shows.query.all()

    for datas in shows:
      show["venue_id"] = datas.venue_id
      show["venue_name"] = datas.venue.name
      show["artist_id"] = datas.artist_id
      show["artist_name"] = datas.artist.name
      show["artist_image_link"] = datas.artist.image_link
      show["start_time"] = datas.start_time
      data.append(show)
      show = {}
    return render_template("pages/shows.html", shows=data)

@app.route("/shows/create")
def create_shows():
  # renders form.
  
  form = ShowForm()
  return render_template("forms/new_show.html", form=form)

@app.route("/shows/create", methods=["POST"])
def create_show_submission():
  # called to create new shows in the db

  form = ShowForm()
  if form.validate_on_submit():
      try:
            show = Shows(artist_id=form.artist_id.data,
                        venue_id=form.venue_id.data,
                        start_time=form.start_time.data)
            db.session.add(show)
            db.session.commit()
            # on successful db insert, flash success
            flash("Show was successfully listed!")
            db.session.close()
            return render_template("pages/home.html")
  
            # on unsuccessful db insert, flash an error instead.
      except:
          db.session.rollback()
          db.session.close()
          flash("An error occurred. Show could not be listed.")
          return render_template("forms/new_show.html", form=form)

  else: 
      flash(form.errors)
      return render_template("forms/new_show.html", form=form)
           

@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
"""
