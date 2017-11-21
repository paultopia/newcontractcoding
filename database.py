from core import db


class Contracts(db.Model):
    __tablename__ = "contracts"
    id = db.Column(db.Integer, primary_key=True)
    contract = db.Column(db.Text())  # text of K
    inprogress = db.Column(db.Boolean())  # flag for state of currently being entered, to avoid accidental duplication.  Need to have a timeout/flush mechanism that cancels inprogress if not entered.
    inprogressstarted = db.Column(db.DateTime())  # last time coding started, for flushing purposes, to enable timeout after an hour.
    firstenteredby = db.Column(db.Integer(), db.ForeignKey('users.id'))
    firstenteredon = db.Column(db.DateTime())
    secondenteredby = db.Column(db.Integer(), db.ForeignKey('users.id'))
    secondenteredon = db.Column(db.DateTime())

    def __init__(self):
        pass  # contracts are going to be added on commandline, not in application code.


class Questions(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text(), index=True, unique=True)

    def __init__(self):
        pass  # questions are going to be added on commandline, not in application code.


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    lastname = db.Column(db.Text(), index=True, unique=True)
    email = db.Column(db.Text(), index=True, unique=True)
    password = db.Column(db.Text())  # will store in clear because this is very unimportant + passwords will be assigned, not user-selected (so no dupe risk).  login will just be lastname + password, all in lowercase.
    isadmin = db.Column(db.Boolean())  # solely for purpose of flushing functionality, I'll have one admin page.

    def __init__(self):
        pass  # users are going to be added on commandline, not in application code.


class Answers(db.Model):
    __tablename__ = "answers"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Integer, db.ForeignKey('questions.id'))
    contract = db.Column(db.Integer, db.ForeignKey('contracts.id'))
    enteredby = db.Column(db.Integer, db.ForeignKey('users.id'))
    answer = db.Column(db.Text())
    # don't need an entered date because can be inferred from enteredby + the enteredon fields in doc database.

    def __init__(self, question, contract, answer, enteredby):
        self.question = question
        self.contract = contract
        self.enteredby = enteredby
        self.answer = answer
