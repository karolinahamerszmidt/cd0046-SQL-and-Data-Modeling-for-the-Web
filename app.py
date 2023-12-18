#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import CSRFProtect
from forms import ShowForm, VenueForm, ArtistForm, SearchForm
from flask_migrate import Migrate
from collections import defaultdict
from datetime import datetime
from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

# We need to expose search_form globally, that's why I use context_processor
# Also, I created SearchForm to be able to handle properly CSRF token
@app.context_processor
def context_processor():
  return dict(search_form=SearchForm())

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues = Venue.query.all()
  
  venues_by_location = defaultdict(list)
  
  for venue in venues:
    key = (venue.city, venue.state)
    venues_by_location[key].append(venue)
  
  data = []
  
  for location, venues in venues_by_location.items():
    data.append({
      "city": location[0],
      "state": location[1],
      "venues": list(
        map(
          lambda venue: {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(venue.shows),
          },
          venues
        )
      )
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  search_query = "%{}%".format(search_term.lower())
  venues = Venue.query.filter(Venue.name.ilike(search_query)).all()

  response = {
    "count": len(venues),
    "data": list(
      map(
        lambda venue: {
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(venue.shows),
        },
        venues
      )
    )
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)

  if venue is None:
      abort(404)

  current_time = datetime.now()
  upcoming_shows = [show for show in venue.shows if show.start_time > current_time]
  past_shows = [show for show in venue.shows if show.start_time <= current_time]

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": list(
      map(
        lambda show: {
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        },
        past_shows
      )
    ),
    "upcoming_shows": list(
      map(
        lambda show: {
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        },
        upcoming_shows
      )
    ),
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)

  if form.validate_on_submit():
    venue = Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genres=','.join(form.genres.data),
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website_link=form.website_link.data,
      seeking_talent=form.seeking_talent.data,
      seeking_description=form.seeking_description.data
    )
    db.session.add(venue)
    
    try:
      db.session.commit()
      flash('Venue ' + venue.name + ' was successfully listed!')
    except Exception as e:
      db.session.rollback()
      flash('An error occurred. Venue could not be listed.')
  else:
    flash('An error occurred. Venue could not be listed.')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    if venue is None:
      abort(404)

    db.session.delete(venue)
    db.session.commit()

  except Exception as e:
    abort(500)

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()

  data = list(
    map(
      lambda artist: {
        "id": artist.id,
        "name": artist.name,
      },
      artists
    )
  )

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  search_query = "%{}%".format(search_term.lower())
  artists = Artist.query.filter(Artist.name.ilike(search_query)).all()
  current_time = datetime.now()

  response = {
    "count": len(artists),
    "data": list(
      map(
        lambda artist: {
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": len([show for show in artist.shows if show.start_time > current_time]),
        },
        artists
      )
    )
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)

  if artist is None:
      abort(404)
  
  current_time = datetime.now()
  upcoming_shows = [show for show in artist.shows if show.start_time > current_time]
  past_shows = [show for show in artist.shows if show.start_time <= current_time]

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
     "past_shows": list(
      map(
        lambda show: {
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        },
        past_shows
      )
    ),
    "upcoming_shows": list(
      map(
        lambda show: {
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        },
        upcoming_shows
      )
    ),
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)

  if artist is None:
      abort(404)

  form = ArtistForm()
  form.name.data = artist.name
  form.genres.data = artist.genres.split(',')
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website_link
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)

  if artist is None:
      abort(404)
  
  form = ArtistForm(request.form)

  if form.validate_on_submit():
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = ','.join(form.genres.data)
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website_link = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    
    try:
      db.session.commit()
      flash('Artist ' + artist.name + ' was successfully updated!')
    except Exception as e:
      db.session.rollback()
      flash('An error occurred. Artist could not be updated.')
  else:
    flash('An error occurred. Artist could not be updated.')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)

  if venue is None:
      abort(404)

  form = VenueForm()
  form.name.data = venue.name
  form.genres.data = venue.genres.split(',')
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)

  if venue is None:
      abort(404)
  
  form = VenueForm(request.form)

  if form.validate_on_submit():
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = ','.join(form.genres.data)
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.website_link = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    
    try:
      db.session.commit()
      flash('Venue ' + venue.name + ' was successfully updated!')
    except Exception as e:
      db.session.rollback()
      flash('An error occurred. Venue could not be updated.')
  else:
    flash('An error occurred. Venue could not be updated.')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)

  if form.validate_on_submit():
    artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=','.join(form.genres.data),
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website_link=form.website_link.data,
      seeking_venue=form.seeking_venue.data,
      seeking_description=form.seeking_description.data
    )
    db.session.add(artist)
    
    try:
      db.session.commit()
      flash('Artist ' + artist.name + ' was successfully listed!')
    except Exception as e:
      db.session.rollback()
      flash('An error occurred. Artist could not be listed.')
  else:
    flash('An error occurred. Artist could not be listed.')

  return render_template('pages/home.html')
  
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()

  data = list(
    map(
      lambda show: {
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        # "2035-04-01T20:00:00.000Z"
        "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
      },
      shows
    )
  )

  return render_template('pages/shows.html', shows=data)
 
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)

  if form.validate_on_submit():
    show = Show(
      venue_id=form.venue_id.data,
      artist_id=form.artist_id.data,
      start_time=form.start_time.data
    )
    db.session.add(show)
    
    try:
      db.session.commit()
      flash('Show was successfully listed!')
    except Exception as e:
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
  else:
    flash('An error occurred. Show could not be listed.')

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
