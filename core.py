from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_heroku import Heroku
from flaskext.markdown import Markdown
core = Flask(__name__)
Markdown(core)
core.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/contracts-part2'  ## get rid of for prod
# need to run createdb contracts-part2
core.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(core)
# heroku = Heroku(core)

# this is horrifying but apparently it's how flask rolls.
# see: http://flask.pocoo.org/docs/0.10/patterns/packages/

import views
