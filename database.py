from core import db


class Contracts(db.Model):
    __tablename__ = "contracts"
    id = db.Column(db.Integer, primary_key=True)
    contract = db.Column(db.Text())  # text of K
    inprogress = db.Column(db.Boolean(), nullable=False)  # flag for state of currently being entered, to avoid accidental duplication.  Need to have a timeout/flush mechanism that cancels inprogress if not entered.  Adding a NOT NULL constraint to make it easier to select not-in-progress columns by just checking for False, not False or None.
    inprogressstarted = db.Column(db.DateTime())  # last time coding started, for flushing purposes, to enable timeout after an hour.
    firstenteredby = db.Column(db.String(50), db.ForeignKey('users.lastname'))
    firstenteredon = db.Column(db.DateTime())
    secondenteredby = db.Column(db.String(50), db.ForeignKey('users.lastname'))
    secondenteredon = db.Column(db.DateTime())

    def __init__(self):
        pass  # contracts are going to be added on commandline, not in application code.


class Questions(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text(), index=True, unique=True)
    validator = db.Column(db.Boolean())  #  if True, then a false answer to this question terminates coding.  implement on client-side.  this is for quick dispatch of non-contract text.  

    def __init__(self):
        pass  # questions are going to be added on commandline, not in application code.


class Users(db.Model):
    __tablename__ = "users"
    lastname = db.Column(db.String(50), primary_key=True)
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
    enteredby = db.Column(db.String(50), db.ForeignKey('users.lastname'))
    answer = db.Column(db.Bool())  # should this be a bool or an integer?
    # don't need an entered date because can be inferred from enteredby + the enteredon fields in doc database.

    def __init__(self, question, contract, answer, enteredby):
        self.question = question
        self.contract = contract
        self.answer = answer
        self.enteredby = enteredby
