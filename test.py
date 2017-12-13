import unittest
import dbops
from flask_testing import TestCase
from core import db
from json import load
# http://pythonhosted.org/Flask-Testing/
# http://pythontesting.net/framework/unittest/unittest-introduction/


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


class TestDbSetup(TestBase):
    def test_list_users(self):
        self.assertEqual(dbops.list_users(), ['gowder', 'student'])

    def test_get_questions(self):
        q = dbops.get_questions()[0]
        self.assertEqual(q["question_id"], '1')
        self.assertEqual(q["questiontext"], "Is this a contract that purports to change or specify an individual's rights or obligations?")

    def test_get_contracts(self):
        gk1 = dbops.fetch_contract('gowder')
        gk2 = dbops.fetch_contract('gowder')
        gk3 = dbops.fetch_contract('gowder')
        sk1 = dbops.fetch_contract('student')
        self.assertEqual(gk1["contract_url"], "http://paul-gowder.com")
        self.assertEqual(gk2["contract_url"], "http://gowder.io")
        self.assertNotEqual(gk1, gk2)
        self.assertIsNone(gk3)
        self.assertIsNone(sk1)
        dbops.force_flush_documents()
        sk2 = dbops.fetch_contract('student')
        self.assertIsNotNone(sk2)
        dbops.force_flush_documents()

class TestViewAccess(TestBase):
    def test_main_page_unauthorized(self):
        self.assertEqual(self.client.get("/").status_code, 401)
        loggedin = self.client.get("/", headers={"Authorization": "Basic Z293ZGVyOnNlY3JldA=="}) # this is the gowder code--- a base64 string of username + : + password I think, judging by this: https://gist.github.com/jarus/1160696 --- gotten by inspecting logged-in request in chrome devtools.
        self.assertEqual(loggedin.status_code, 200)

if __name__ == '__main__':
    unittest.main()
