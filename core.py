from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku
from flaskext.markdown import Markdown  # TODO: add this extension with pipenv install Flask-Markdown
core = Flask(__name__)
Markdown(core)
core.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(core)
heroku = Heroku(core)