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

# hanging onto link for postgres role setup https://www.codementor.io/devops/tutorial/getting-started-postgresql-server-mac-osx 
