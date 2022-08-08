# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from email.policy import default
from os import abort
from traceback import print_tb
from black import err
from sqlalchemy import exc
import json
from sqlalchemy.exc import SQLAlchemyError
import sys
from typing import final
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    jsonify,
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from model import db,Artist,Venue,Show

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")

app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route("/")
def index():
  artists = Artist.query.order_by(Artist.created_at.desc()).limit(10).all()
  venues = Venue.query.order_by(Venue.created_at.desc()).limit(10).all()
  return render_template("pages/home.html",artists=artists, venues= venues)


#  Venues
#  ----------------------------------------------------------------

@app.route("/venues")
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    venue = Venue.query.all()
    return render_template("pages/venues.html", areas=venue)

@app.route("/venues/search", methods=["POST"])
def search_venues():
    search_result = {}
    try:
        searchTerm = request.form.get("search_term")
        search_data = Venue.query.filter(
            Venue.name.ilike("%{}%".format(searchTerm))
            | Venue.city.ilike("%{}%".format(searchTerm))
            | Venue.state.ilike("%{}%".format(searchTerm))
        ).all()
        data = []
        for venue in search_data:
            data.append({"id": venue.id, "name": venue.name})
        search_result = {"count": len(search_data), "data": data}
    except SQLAlchemyError as e:
        print(e)
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    return render_template(
        "pages/search_venues.html",
        results=search_result,
        search_term=request.form.get("search_term"),
    )

@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    try:
        # shows the venue page with the given venue_id
        venue = Venue.query.filter_by(id=venue_id).first()
        past_show = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
        upcoming_show = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "city": venue.city,
            "state": venue.state,
            "address": venue.address,
            "phone": venue.phone,
            "website": venue.website_link,
            "image_link": venue.image_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.description,
            "past_shows": past_show,
            "past_shows_count": len(past_show),
            "upcoming_shows": upcoming_show,
            "upcoming_shows_count": len(upcoming_show),
        }
    except SQLAlchemyError as e:
        print(e)
    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)

@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form)
    if form.validate():
        try:
            name = form.name.data
            city = form.city.data
            state = form.state.data
            address = form.address.data
            genres = form.genres.data
            phone = form.phone.data
            facebook_link = form.facebook_link.data
            image_link = form.image_link.data
            website_link = form.website_link.data
            seeking_description = form.seeking_description.data
            seeking_talent = form.seeking_talent.data

            venue = Venue(
                name=name,
                city=city,
                state=state,
                address=address,
                phone=phone,
                facebook_link=facebook_link,
                image_link=image_link,
                website_link=website_link,
                description=seeking_description,
                seeking_talent=seeking_talent,
                genres=genres,
                created_at =  datetime.now()
            )

            db.session.add(venue)
            db.session.commit()
        except:
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
         # on successful db insert, flash success
        flash("Venue " + request.form["name"] + " was successfully listed!")
    else:
        flash(
            "An error occurred. Venue " + request.form["name"] + " could not be listed."
        )
    return render_template("pages/home.html")

#  Edit Venue
#  ----------------------------------------------------------------

@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).first()
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.website_link.data = venue.website_link
    form.image_link.data = venue.image_link
    form.facebook_link.data = venue.facebook_link
    form.seeking_description.data = venue.description
    form.seeking_talent.data = venue.seeking_talent
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form=form, venue=venue)

@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    if form.validate():
        try:
            venue = db.session.query(Venue).get(venue_id)
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.genres = form.genres.data
            venue.phone = form.phone.data
            venue.facebook_link = form.facebook_link.data
            venue.image_link = form.image_link.data
            venue.website_link = form.website_link.data
            venue.seeking_description = form.seeking_description.data
            venue.seeking_talent = form.seeking_talent.data

            db.session.commit()
        except:
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        # on successful db insert, flash success
        flash("Venue " + request.form["name"] + " was successfully updated!")
    else:
        flash(
            "An error occurred. Venue "
            + request.form["name"]
            + " could not be updated."
        )
    return redirect(url_for("show_venue", venue_id=venue_id))

@app.route("/venues/delete/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    error = False
    try:
        shows = Show.query.filter_by(venue_id=venue_id).all()
        for show in shows:
            show_delete = db.session.merge(show)
            db.session.delete(show_delete)
        venue = Venue.query.filter_by(id=venue_id).first()
        venue_delete = db.session.merge(venue)
        db.session.delete(venue_delete)
        db.session.commit()
    except SQLAlchemyError as e:
        print(e)
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash("Venue could not be deleted")
        abort(500)
    else:
        flash("Venue deleted !")
        return jsonify({"success": True})
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    artists = Artist.query.all()
    return render_template("pages/artists.html", artists=artists)

@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_result = {}
    try:
        searchTerm = request.form.get("search_term")
        search_data = Artist.query.filter(
            Artist.name.ilike("%{}%".format(searchTerm))
            | Artist.city.ilike("%{}%".format(searchTerm))
            | Artist.state.ilike("%{}%".format(searchTerm))
        ).all()
        data = []
        for artist in search_data:
            data.append({"id": artist.id, "name": artist.name})
        search_result = {"count": len(search_data), "data": data}
    except SQLAlchemyError as e:
        print(e)
    return render_template(
        "pages/search_artists.html",
        results=search_result,
        search_term=request.form.get("search_term", ""),
    )

@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    try:
        artist = Artist.query.filter_by(id=artist_id).first()
        past_show = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
        upcoming_show = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
        data = {
            "id": artist.id,
            "name": artist.name,
            "city": artist.city,
            "state": artist.state,
            "genres": artist.genres,
            "image_link": artist.image_link,
            "website": artist.website_link,
            "facebook_link": artist.facebook_link,
            "phone": artist.phone,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.description,
            "upcoming_shows": upcoming_show,
            "past_shows": past_show,
            "upcoming_shows_count": len(upcoming_show),
            "past_shows_count": len(past_show),
        }
    except SQLAlchemyError as e:
        print(e)

    return render_template("pages/show_artist.html", artist=data)


#  Create Artist
#  ----------------------------------------------------------------

@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)

@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)
    if form.validate():
        try:
            name = form.name.data
            city = form.city.data
            state = form.state.data
            genres = form.genres.data
            phone = form.phone.data
            facebook_link = form.facebook_link.data
            image_link = form.image_link.data
            website_link = form.website_link.data
            seeking_description = form.seeking_description.data
            seeking_venue = form.seeking_venue.data
            artist = Artist(
                name=name,
                city=city,
                state=state,
                phone=phone,
                facebook_link=facebook_link,
                image_link=image_link,
                website_link=website_link,
                description=seeking_description,
                seeking_venue=seeking_venue,
                genres=genres,
            )

            db.session.add(artist)
            db.session.commit()
        except:
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        # on successful db insert, flash success
        flash("Artist " + request.form["name"] + " was successfully listed!")
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    else:
        flash("An error occurred.")
        print(form.errors)

    return render_template("pages/home.html")

#  Edit Artist
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).first()
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.website_link.data = artist.website_link
    form.image_link.data = artist.image_link
    form.facebook_link.data = artist.facebook_link
    form.seeking_description.data = artist.description
    form.seeking_venue.data = artist.seeking_venue
    return render_template("forms/edit_artist.html", form=form, artist=artist)

@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    if form.validate():
        try:
            artist = db.session.query(Artist).get(artist_id)
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.genres = form.genres.data
            artist.phone = form.phone.data
            artist.facebook_link = form.facebook_link.data
            artist.image_link = form.image_link.data
            artist.website_link = form.website_link.data
            artist.seeking_description = form.seeking_description.data
            artist.seeking_venue = form.seeking_venue.data
            db.session.commit()
        except SQLAlchemyError as e:
            print(e)
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        flash("Artist " + request.form["name"] + " was successfully updated!")
    else:
        flash(
            "An error occurred. Artist "
            + request.form["name"]
            + " could not be updated."
        )
    return redirect(url_for("show_artist", artist_id=artist_id))

#  Shows
#  ----------------------------------------------------------------

@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    shows = Show.query.all()
    data = []
    for item in shows:
        data.append(
            {
                "venue_id": item.venue_id,
                "venue_name": item.venue.name,
                "artist_id": item.artist_id,
                "artist_name": item.artist.name,
                "artist_image_link": item.artist.image_link,
                "start_time": item.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    return render_template("pages/shows.html", shows=data)

@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)

@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    error = False
    try:
        artist_id = request.form["artist_id"]
        venue_id = request.form["venue_id"]
        start_time = request.form["start_time"]
        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

        # called to create new shows in the db, upon submitting new show listing form
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    # TODO: on unsuccessful db insert, flash an error instead.
    if error:
        flash("An error occurred. Show could not be listed.")
    else:
        # on successful db insert, flash success
        flash("Show was successfully listed!")

    return render_template("pages/home.html")

@app.route('/show/search', methods=["POST"])
def search_shows():
    search_term = request.form.get('search_term')
    search_show = Show.query.all()
    data=[]
    for show in search_show:
        if((search_term.lower() in show.artist.name.lower()) | (search_term.lower() in show.venue.name.lower()) ):
            data.append({
                'artist_name':show.artist.name,
                'venue_name':show.venue.name,
                'artist_image_link':show.artist.image_link,
                'start_time':show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                'venue_id':show.venue_id,
                'artist_id':show.artist_id
            })

    return render_template('/pages/search_show.html', shows=data, search_term = search_term , search_count = len(data))
#  Error
#  ----------------------------------------------------------------

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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
