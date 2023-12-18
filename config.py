import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connection to my local database
SQLALCHEMY_DATABASE_URI = 'postgresql://myuser:mypassword@localhost:5432/fyyur'

# Example secret key used for CSRF token protection
SECRET_KEY = 'example-secret-key'
