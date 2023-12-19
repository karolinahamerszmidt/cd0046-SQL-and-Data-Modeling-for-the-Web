from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, ValidationError
from wtforms.validators import DataRequired, AnyOf, URL, Optional
from enums import Genre, State
import re

def is_valid_phone(number):
    regex = re.compile(r'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
    return regex.match(number)

def validate_phone(self,field):
    if not is_valid_phone(field.data):
        raise ValidationError('Invalid phone.')

def validate_state(self,field):
        if field.data not in dict(State.choices()).keys():
            raise ValidationError('Invalid state. ')

def validate_genres(self,field):
    if not set(field.data).issubset(dict(Genre.choices()).keys()):
        raise ValidationError('Invalid genres. ')

class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id',
        validators=[DataRequired()],
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired()],
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), validate_state],
        choices=State.choices()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone',
        validators=[Optional(), validate_phone]
    )
    image_link = StringField(
        'image_link',
        validators=[Optional(), URL()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(), validate_genres],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(), URL()]
    )
    website_link = StringField(
        'website_link',
        validators=[Optional(), URL()]
    )

    seeking_talent = BooleanField('seeking_talent')

    seeking_description = StringField(
        'seeking_description',
        validators=[Optional()]
    )



class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), validate_state],
        choices=State.choices()
    )
    phone = StringField(
        'phone',
        validators=[Optional(), validate_phone]
    )
    image_link = StringField(
        'image_link',
        validators=[Optional(), URL()]
    )
    genres = SelectMultipleField(
        'genres',
        validators=[DataRequired(), validate_genres],
        choices=Genre.choices()
     )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(), URL()]
     )

    website_link = StringField(
        'website_link',
        validators=[Optional(), URL()]
     )

    seeking_venue = BooleanField('seeking_venue')

    seeking_description = StringField(
            'seeking_description',
            validators=[Optional()]
     )

class SearchForm(FlaskForm):
    search_term = StringField('search_term', validators=[DataRequired()])
