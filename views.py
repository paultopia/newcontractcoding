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
    ln = lastname.lower()
    if ln in db.list_users():
        hashed_pw = db.find_hashed_password(ln)
        return bcrypt.checkpw(password.encode('utf8'), hashed_pw.encode('utf8'))  # not sure whether this wants bytes or not, might have to call .encode('utf8') on either or both 
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
    user_name = auth.username()
    questions = db.get_questions()
    contract = db.fetch_contract(user_name)
    if contract:
        data = {"questions": questions, "contract": contract}
        return render_template("dataentry.html", templatedata=data)
    else:
        return "I don't have a contract for you to enter data on right now. Please contact Gowder and let him know this happened."


@core.route("/enter-data", methods=['POST'])
@auth.login_required
def add_data():
    questions = [x["question_id"] for x in db.get_questions()]
    answers = {}
    for q in questions:
        answers[int(q)] = properbool(request.form[q])
    db.add_answers(answers, int(request.form["contract_id"]), auth.username())
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
    return render_template("admin.html")


@core.route("/add_user", methods=['POST'])  # does not permit adding admin users.  do that from psql or something. there should only be one admin user anyway.
@must_be_admin
@auth.login_required
def add_user():
    ln = db.add_user(request.form["lastname"],
                     request.form["email"],
                     request.form["clear_password"],
                     False)
    return 'Successfully added {}!  <a href="{}">Carry out another admin task?</a>'.format(ln, url_for("admin"))

# NOT YET TESTED MEANINGFULLY
@core.route("/flush_pending", methods=['POST'])
@must_be_admin
@auth.login_required
def flush_pending():
    success = db.flush_documents()
    if success:
        return 'Successfully flushed pending documents!  <a href="{}">Carry out another admin task?</a>'.format(url_for("admin"))
    return 'Did not successfully flush pending documents. <a href="{}">Try again, or carry out another admin task?</a>'.format(url_for("admin"))


@core.route("/add_contract", methods=['POST'])
@must_be_admin
@auth.login_required
def add_contract():
    contract = {"contract": request.form["contract"], "url": request.form["url"]}
    db.add_contract(contract)
    return 'Successfully added a contract!  <a href="{}">Carry out another admin task?</a>'.format(url_for("admin"))
