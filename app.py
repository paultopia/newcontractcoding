from flask import Flask, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from json import dumps, load
from datetime import datetime
from random import choice
from copy import copy
import sys
from flask_heroku import Heroku

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
db = SQLAlchemy(app)


class Contracts(db.Model):
    __tablename__ = "contracts"
    id = db.Column(db.Integer, primary_key=True)

    def __init__(self):
        pass


@app.route("/")
def root():
    return "Please go to the personal web address that I gave you. <br>-PG"



if __name__ == '__main__':
    #app.debug = True
    app.run()

