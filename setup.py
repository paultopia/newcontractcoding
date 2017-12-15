import dbops
import json
import sqlalchemy
from distutils.util import strtobool
from core import db

instructions_for_adding_contracts = """
To add contracts, go to psql and run:

\copy contracts from '/absolute/path/to/contracts.csv' with (format csv);

then

select setval('contracts_id_seq', max(id)) from contracts;

"""


def create_db():
    try:
        dbops.count_contracts()  # if this fails, there's no db...
        print("Database already exists, checking questions...")
    except:
        db.create_all()
        print("Created database!  Now to check questions...")


def add_questions():
    count = dbops.count_questions()
    if count > 0:
        print("You already have questions. If you want more, delete the existing set first.  Now looking for administrator...")
    else:
        with open("questions.json") as q:
            questions = json.load(q)
            dbops.add_questions(questions)
            print("Added questions from file.")


def add_admin_user():
    admins = dbops.list_administrators()
    if len(admins) > 0:
        print("You already have an administrator.")
        try:
            addmore = strtobool(input("Add another administrator? [y/N]"))
        except ValueError:
            addmore = False
    else:
        addmore = True
    if addmore:
        print("Ok, let's add an administrator!")
        username = input("Give me a last name for the administrator").lower()
        email = input("What's the administrator's e-mail?")
        password = input("Give me a password for the administrator")
        print("Ok, your administrator username is {} and password is {} for e-mail {}".format(username, password, email))
        dbops.add_user(username, email, password, isadmin=True)


def add_contracts():
    count = dbops.count_contracts()
    if count > 0:
        print("You already have contracts in the database.")
    else:
        print(instructions_for_adding_contracts)


def setup():
    create_db()
    add_questions()
    add_admin_user()
    add_contracts()


if __name__ == '__main__':
    setup()
    print("setup tasks done!")
