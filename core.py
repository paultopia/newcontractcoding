from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku
core = Flask(__name__)
core.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(core)
heroku = Heroku(core)
