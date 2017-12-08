import dbops
import requests


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
    from json import load
    with open("testcontracts.json") as tc:
        dbops.add_contracts(load(tc))
    with open("testusers.json") as tu:
        dbops.add_users(load(tu))
    with open("testquestions.json") as tu:
        dbops.add_questions(load(tu))
    
