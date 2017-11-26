import bcrypt
from core import core
frpm dbops import get_questions, fetch_contract, add_answers, list_users, find_hashed_password, is_admin
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_pw(lastname, password):
    if lastname in list_users():
        hashed_pw = find_hashed_password(lastname)
        return bcrypt.checkpw(password, hashed_password)
    return False

@core.route("/")
@auth.login_required
def root():
    lastname = auth.username()
    """this route will ask for login using flask-httpauth and then offer a coding page, or, if login is me, a coding/admin page."""
    return "TODO"

@core.route("enter-data")
@auth.login_required
def add_data():
    """this route will enter data in the database, then offer user a choice to get another doc or quit."""
    return "TODO"

@core.route("admin")
@auth.login_required
def admin():
    if is_admin(auth.username()):
        return "TODO: page goes here"
    return "Not authorized."
