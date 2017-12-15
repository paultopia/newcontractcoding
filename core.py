import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flaskext.markdown import Markdown
is_local = bool(os.environ.get("NEW_CONTRACT_CODING_LOCAL"))
if not is_local:
    from flask_heroku import Heroku
core = Flask(__name__)
Markdown(core)
if is_local:
    core.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/contracts-part2'
# need to run createdb contracts-part2
core.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(core)
if not is_local:
    heroku = Heroku(core)

# this is horrifying but apparently it's how flask rolls.
# see: http://flask.pocoo.org/docs/0.10/patterns/packages/

import views
