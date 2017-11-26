import bcrypt
from core import core
import dbops as db
from flask_httpauth import HTTPBasicAuth
from flask import render_template, request, url_for
from functools import wraps
from distutils.util import strtobool

auth = HTTPBasicAuth()


def properbool(s):   # https://docs.python.org/3/distutils/apiref.html?highlight=strtobool#distutils.util.strtobool  can give it lowercase "true" or "false" or 1 and 0
    return(bool(strtobool(s)))  # this would probably work fine with ints rather than bool types, but I don't like implicit coercion on the way into the database.


@auth.verify_password
def verify_pw(lastname, password):
    if lastname in db.list_users():
        hashed_pw = db.find_hashed_password(lastname)
        return bcrypt.checkpw(password, hashed_password)
    return False

###########################
#
# USER ROUTES
#
###########################


@core.route("/")
@auth.login_required
def coding():
    """this route will offer a coding page."""
    lastname = auth.username()
    return "TODO"


@core.route("/enter-data")
@auth.login_required
def add_data():
    questions = [x.id for x in db.get_questions()]
    answers = {}
    for q in questions:
        answers[q] = properbool(request.form[q])
    db.add_answers(answers, request.form["contract_id"], auth.username())
    # maybe log here?
    return 'To enter another contract, <a href="{}">click here!</a>.  If you are done, just close the browser window. <b>Please do not click the link unless you are ready to enter another contract.</b>'.format(url_for("coding"))

###########################
#
# ADMIN ROUTES
#
###########################


def must_be_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if db.is_admin(auth.username()):
            return f(*args, **kwargs)
        return "Not authorized."
    return wrapper
# I'm not sure that this is going to work to preserve the context with the username call.
# if it doesn't work, I'll just stick this check into each admin function.


@core.route("/admin")
@must_be_admin
@auth.login_required
def admin():
    return "TODO: page goes here"


@core.route("/db.add_user")
@must_be_admin
@auth.login_required
def db.add_user_view():
    ln = db.add_user(request.form["lastname"],
                  request.form["email"],
                  request.form["clear_password"],
                  properbool(request.form["isadmin"]))
    return 'Successfully added {}!  <a href="{}">Carry out another admin task?</a>'.format(ln, url_for("admin"))


@core.route("/flush_pending")
@must_be_admin
@auth.login_required
def flush_pending():
    success = db.flush_documents()
    if success:
        return 'Successfully flushed pending documents!  <a href="{}">Carry out another admin task?</a>'.format(url_for("admin"))
    return 'Did not successfully flush pending documents. <a href="{}">Try again, or carry out another admin task?</a>'.format(url_for("admin"))

# I'm going to need a setup.py to do initial setup.  I can probably just do heroku run python and then from setup import setup and so forth.  just pass a url for the initial sqlite database for docs and json for users.
