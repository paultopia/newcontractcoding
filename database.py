from core import db


class Contracts(db.Model):
    __tablename__ = "contracts"
    id = db.Column(db.Integer, primary_key=True)
    contract = db.Column(db.Text())  # text of K
    url = db.Column(db.Text())
    firstadded = db.Column(db.Text())  # this is actually going to be a serialized datetime but I won't ever need it programmatically, so I'll leave it as text.
    firstaddedby = db.Column(db.Text())
    inprogress = db.Column(db.Boolean(), nullable=False)
    # flag for state of currently being entered, to avoid accidental duplication.  Need to have a timeout/flush mechanism that cancels inprogress if not entered.  Adding a NOT NULL constraint to make it easier to select not-in-progress columns by just checking for False, not False or None.
    inprogressstarted = db.Column(db.DateTime())  # last time coding started, for flushing purposes, to enable timeout after an hour.
    firstenteredby = db.Column(db.String(50), db.ForeignKey('users.lastname'))
    firstenteredon = db.Column(db.DateTime())
    secondenteredby = db.Column(db.String(50), db.ForeignKey('users.lastname'))
    secondenteredon = db.Column(db.DateTime())

    def __init__(self, contract, url, firstadded, firstaddedby):
        self.contract = contract
        self.url = url
        self.firstadded = firstadded
        self.firstaddedby = firstaddedby
        self.inprogress = False
        self.inprogressstarted = None
        self.firstenteredby = None
        self.firstenteredon = None
        self.secondenteredby = None
        self.secondenteredon = None


class Questions(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    questiontext = db.Column(db.Text(), index=True, unique=True)
    explanation = db.Column(db.Text())

    def __init__(self, questiontext, explanation):
       self.questiontext = questiontext
       self.explanation = explanation


class Users(db.Model):
    __tablename__ = "users"
    lastname = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.Text(), index=True, unique=True)
    password = db.Column(db.Text())  # passwords will be assigned, not user-selected.  login will just be lastname + password, all in lowercase.
    isadmin = db.Column(db.Boolean())  # I'll need an admin page with functionality to add documents, add users, and flush the in-progress docs.  Maybe also to check status?  that can just be raw sql in psql though.

    def __init__(self, lastname, email, password, isadmin):
        self.lastname = lastname.lower()
        self.email = email
        self.password = password
        self.isadmin = isadmin


class Answers(db.Model):
    __tablename__ = "answers"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Integer, db.ForeignKey('questions.id'))
    contract = db.Column(db.Integer, db.ForeignKey('contracts.id'))
    enteredby = db.Column(db.String(50), db.ForeignKey('users.lastname'))
    answer = db.Column(db.Boolean())  # should this be a bool or an integer?
    # don't need an entered date because can be inferred from enteredby + the enteredon fields in doc database.

    def __init__(self, question, contract, answer, enteredby):
        self.question = question
        self.contract = contract
        self.answer = answer
        self.enteredby = enteredby
