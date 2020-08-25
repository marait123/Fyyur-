#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask import jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
import utility
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500),default="https://www.nomadfoods.com/wp-content/uploads/2018/08/placeholder-1-e1533569576673.png")
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship("Show", backref ="venue",lazy=True)
    website = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    @hybrid_property
    def upcoming_shows(self):
      return Show.query.filter(Show.start_time >= datetime.now()).filter(Show.venue_id==self.id)
    @hybrid_property
    def upcoming_shows_count(self):
      return Show.query.filter(Show.start_time >= datetime.now()).filter(Show.venue_id==self.id).count()
    @hybrid_property
    def past_shows(self):
      return Show.query.filter(Show.start_time < datetime.now()).filter(Show.venue_id==self.id)
    @hybrid_property
    def past_shows_count(self):
      return Show.query.filter(Show.start_time < datetime.now()).filter(Show.venue_id==self.id).count()

    
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500),default="https://www.nomadfoods.com/wp-content/uploads/2018/08/placeholder-1-e1533569576673.png")
    facebook_link = db.Column(db.String(120))
    shows = db.relationship("Show", backref ="artist",lazy=True)
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    
    @hybrid_property
    def upcoming_shows(self):
      return Show.query.filter(Show.start_time >= datetime.now()).filter(Show.artist_id==self.id)
    @hybrid_property
    def upcoming_shows_count(self):
      return Show.query.filter(Show.start_time >= datetime.now()).filter(Show.artist_id==self.id).count()
    @hybrid_property
    def past_shows(self):
      return Show.query.filter(Show.start_time < datetime.now()).filter(Show.artist_id==self.id)
    @hybrid_property
    def past_shows_count(self):
      return Show.query.filter(Show.start_time < datetime.now()).filter(Show.artist_id==self.id).count()



class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.DateTime)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  
  if type(value) == type(datetime.now()):
    value = str(value)
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"

  return babel.dates.format_datetime(date, format)
    

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue. 
  areas = []
  # separate the venues by area
  for city,state in db.session.query(Venue.city,Venue.state).distinct():
    area = {}
    area['city'] = city
    area['state'] = state
    area_venues = Venue.query.filter(Venue.city == city).filter(Venue.state==state)
    area['venues'] = area_venues
    areas.append(area)
  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  response = {}
  search = "%{}%".format(request.form.get('search_term', ''))
  found_venues = Venue.query.filter(Venue.name.like(search))
  response['data'] = found_venues.all()
  response['count'] = found_venues.count()
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.get(venue_id)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  form = VenueForm()
  try:
    # TODO: make validation fails due to csrf token
    # validation doesn't work

    genres = request.form.getlist('genres')
    data = dict(request.form)
    data['genres'] = utility.join_array(genres)
    venue = Venue(**data)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    
  except:
    db.session.rollback()
    error = sys.exc_info()
    print(error)
    flash('Error: Venue was not added!')
  finally:
    db.session.close()
   # on successful db insert, flash success
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = None
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash("successfully deleted the venue")
  except:
    flash("couldn't delete the venue due to an error")
    db.session.rollback()
    print(sys.exc_info)
    error = {}
    error['status'] = 400
    error['message'] = sys.exc_info()
  finally:
    db.session.close()
  if not error:
    return jsonify(url=url_for('index'))
  else:
    return jsonify(url=url_for('index'),error=error['message']), 400
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database 
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  response = {}
  search = "%{}%".format(request.form.get('search_term', ''))
  found_artists = Artist.query.filter(Artist.name.like(search))
  response['data'] = found_artists.all()
  response['count'] = found_artists.count()
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = Artist.query.get(artist_id)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):  
  artist = Artist.query.get(artist_id)
  form = ArtistForm()
  form_attributes = ["name", "city","state","phone","genres","facebook_link"]
  utility.map_attribute(artist,form,form_attributes)
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:    
    artist = Artist.query.get(artist_id)
    data = request.form.to_dict()
    data['genres'] =  utility.join_array(request.form.getlist('genres'))
    for field in data:
      setattr(artist,field,data[field])
    db.session.commit()
    flash("artist was added successfully")
  except:
    db.session.rollback()
    print(sys.exc_info)
    flash("Error: an error happend while modifying artist")
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm()
  form_attributes = ["name", "city","state","address","phone","genres","facebook_link"]
  utility.map_attribute(venue,form,form_attributes)   
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:    
    venue = Venue.query.get(venue_id)
    data = request.form.to_dict()
    data['genres'] =  utility.join_array(request.form.getlist('genres'))
    for field in data:
      setattr(venue,field,data[field])
    db.session.commit()
    flash("venue was modified successfully")
  except:
    db.session.rollback()
    print(sys.exc_info)
    flash("Error: an error happend while modifying venue")
  finally:
    db.session.close()  
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    data = dict(request.form)
    data['genres'] = utility.join_array(request.form.getlist('genres'))
    artist = Artist(**data)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Error Occured while adding the Artist')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = Show.query.all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    data = dict(request.form)
    show = Show(**data)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('Error: last show was not added!')
  finally:
    db.session.close()
  # on successful db insert, flash success
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
