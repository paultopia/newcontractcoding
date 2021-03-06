import os
os.environ["NEW_CONTRACT_CODING_LOCAL"] = "true"
# have to start with this in order to guarantee that app object creation will be in local config.  It doesn't seem to work from here, though, for some weird reason...

import dbops
import requests
from core import db



def add_documents(docsjsonurl):
    dbops.add_contracts(requests.get(docsjsonurl).json())


def add_questions(questionsjsonurl):
    dbops.add_questions(requests.get(questionsjsonurl).json())


def add_users(usersjsonurl):
    dbops.add_users(requests.get(usersjsonurl).json())


def setup(docs_url, questions_url, users_url):
    add_documents(docs_url)
    add_questions(questions_url)
    add_users(users_url)
    print("set up!")


def test_setup():
    db.create_all()
    from json import load
    with open("testcontracts.json") as tc:
        dbops.add_contracts(load(tc))
    with open("testusers.json") as tu:
        dbops.add_users(load(tu))
    with open("testquestions.json") as tq:
        dbops.add_questions(load(tq))
    
if __name__ == '__main__':
    test_setup()
    print("setup!")
