import unittest
import dbops
import sqlalchemy
from flask_testing import TestCase
from core import db
from json import load
from base64 import b64encode
from database import Contracts
from time import sleep
from datetime import datetime


def make_auth_header(name, password):  # this is based off the previous example
    bs = bytes(name + ":" + password, "utf-8")
    b64 = b64encode(bs).decode("utf-8")
    return {"Authorization": "Basic " + b64}

def cycle():
    db.session.remove()
    db.drop_all()
    db.create_all()
    with open("testcontracts.json") as tc:
        dbops.add_contracts(load(tc))
    with open("testusers.json") as tu:
        dbops.add_users(load(tu))
    with open("questions.json") as tq:
        dbops.add_questions(load(tq))


def setUpModule():
    db.create_all()
    with open("testcontracts.json") as tc:
        dbops.add_contracts(load(tc))
    with open("testusers.json") as tu:
        dbops.add_users(load(tu))
    with open("questions.json") as tq:
        dbops.add_questions(load(tq))


def tearDownModule():
    db.session.remove()
    db.drop_all()


class TestBase(TestCase):

    def create_app(self):
        from core import core
        core.config['TESTING'] = True
        return core


class TestStateful(TestBase):  # adding class setup and teardown methods for test classes that mutate database and require isolation.  classes that need isolation can just inherit from this.
    @classmethod
    def setUpClass(cls):
        cycle()

    @classmethod
    def tearDownClass(cls):
        cycle()

