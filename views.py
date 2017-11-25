from core import core
frpm dbops import get_questions, fetch_contract, add_answers, list_users, find_password
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.get_password
def get_pw(lastname):
    if lastname in list_users():
        return find_password(lastname)
    return None

@core.route("/")
@auth.login_required
def root():
    lastname = auth.username()
    """this route will ask for login using flask-httpauth and then offer a coding page, or, if login is me, a coding/admin page."""
    return "TODO"

@core.route("enter-data")
def add_data():
    """this route will enter data in the database, then offer user a choice to get another doc or quit."""
    return "TODO"