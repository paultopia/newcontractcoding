import unittest
import dbops
from flask_testing import TestCase
from core import db
from json import load
# http://pythonhosted.org/Flask-Testing/
# http://pythontesting.net/framework/unittest/unittest-introduction/

gowder_auth = {"Authorization": "Basic Z293ZGVyOnNlY3JldA=="}
# this is the gowder code--- a base64 string of username + : + password I think, judging by this: https://gist.github.com/jarus/1160696 --- gotten by inspecting logged-in request in chrome devtools.


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


class TestStateful(TestBase):  # adding class setup and teardown methods for test classes that mutate database and require isolation
    @classmethod
    def setUpClass(cls):
        cycle()

    @classmethod
    def tearDownClass(cls):
        cycle()


class TestDbSetup(TestBase):

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
        loggedin = self.client.get("/", headers=gowder_auth)
        self.assertEqual(loggedin.status_code, 200)
        # should add second method for authorized.  also should test auth for admin page with and without admin identity. i.e. need to test that student login can't get admin routes


class TestAddUser(TestStateful):

    def test_add_user(self):
        rsp = self.client.post("/add_user", headers=gowder_auth, data={"lastname": "stub", "email": "none@none.net", "clear_password": "0000"})
        self.assertEqual(rsp.data, b'Successfully added stub!  <a href="/admin">Carry out another admin task?</a>')
        self.assertEqual(dbops.list_users(), ['gowder', 'stub', 'student'])


class TestAddDoc(TestStateful):

    def test_add_document(self):  # should switch to do this from student
        rsp = self.client.post("/enter-data", headers=gowder_auth, data={"1": "no", "contract_id": "1"})
        answerlist = dbops.pick_contract(1).answers
        self.assertEqual({answerlist[0].id: answerlist[0].answer,
                          answerlist[1].id: answerlist[1].answer},
                         {1: False, 2: True})
        self.assertEqual(rsp.data, b'To enter another contract, <a href="/">click here!</a>.  If you are done, just close the browser window. <b>Please do not click the link unless you are ready to enter another contract.</b>')


if __name__ == '__main__':
    unittest.main()
