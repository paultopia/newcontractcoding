from core import core
frpm dbops import get_questions, fetch_contract, add_answers


@core.route("/")
def root():
    """this route will ask for login using flask-httpauth and then offer a coding page, or, if login is me, a coding/admin page."""
    return "TODO"

@core.route("enter-data")
def add_data():
    """this route will enter data in the database, then offer user a choice to get another doc or quit."""
    return "TODO"