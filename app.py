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
    contract = db.Column(db.Text())  # text of K
    inprogress = db.Column(db.Boolean())  # flag for state of currently being entered, to avoid accidental duplication.  Need to have a timeout/flush mechanism that cancels inprogress if not entered.
    inprogressstarted = db.Column(db.DateTime())  # last time coding started, for flushing purposes, to enable timeout after an hour.
    firstenteredby = db.Column(db.Integer())  # CONNECT TO USERID
    firstenteredon = db.Column(db.DateTime())
    secondenteredby = db.Column(db.Integer())  # CONNECT TO USERID
    secondenteredon = db.Column(db.DateTime())

    def __init__(self):
        pass  # contracts are going to be added on commandline, not in application code.


class Questions(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text())

    def __init__(self):
        pass  # questions are going to be added on commandline, not in application code.


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.Text())
    lastname = db.Column(db.Text())
    email = db.Column(db.Text())
    password = db.Column(db.Text())  # will store in clear because this is very unimportant + passwords will be assigned, not user-selected (so no dupe risk).  login will just be lastname + password, all in lowercase.
    isadmin = db.Column(db.Boolean())  # solely for purpose of flushing functionality, I'll have one admin page.

    def __init__(self):
        pass  # users are going to be added on commandline, not in application code.


class Answers(db.Model):
    __tablename__ = "answers"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Integer)  # CONNECT TO QUESTIONS TABLE
    contract = db.Column(db.Integer)  # CONNECT TO CONTRACTS TABLE
    enteredby = db.Column(db.Integer) # CONNECT TO USERS TABLE
    answer = db.Column(db.Text())
    # don't need an entered date because can be inferred from enteredby + the enteredon fields in doc database.

    def __init__(self, question, contract, answer, enteredby):
        self.question = question
        self.contract = contract
        self.enteredby = enteredby
        self.answer = answer


@app.route("/")
def root():
    return "Please go to the personal web address that I gave you. <br>-PG"



if __name__ == '__main__':
    #app.debug = True
    app.run()

