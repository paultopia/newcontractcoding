import unittest
import dbops
from flask_testing import TestCase
from core import db
from json import load
# http://pythonhosted.org/Flask-Testing/
# http://pythontesting.net/framework/unittest/unittest-introduction/

class TestBase(TestCase):

    def create_app(self):
        from core import core
        core.config['TESTING'] = True
        return core

    def setUp(self):
        db.create_all()
        with open("testcontracts.json") as tc:
            dbops.add_contracts(load(tc))
        with open("testusers.json") as tu:
            dbops.add_users(load(tu))
        with open("testquestions.json") as tq:
            dbops.add_questions(load(tq))

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestDbSetup(TestBase):
    def test_list_users(self):
        self.assertEqual(dbops.list_users(), ['gowder', 'student'])

    def test_fail_users(self):
        self.assertEqual(dbops.list_users(), ['gowderNOT', 'student'])


if __name__ == '__main__':
    unittest.main()
