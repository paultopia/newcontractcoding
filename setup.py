import dbops as db
import requests


def add_documents(docsjsonurl):
    db.add_contracts(requests.get(docsjsonurl).json())


def add_questions(questionsjsonurl):
    db.add_questions(requests.get(questionsjsonurl).json())


def add_users(usersjsonurl):
    db.add_questions(requests.get(usersjsonurl).json())


def setup(docs_url, questions_url, users_url):
    add_documents(docs_url)
    add_questions(questions_url)
    add_users(users_url)
    print("set up!")
