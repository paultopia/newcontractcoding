import os
os.environ["NEW_CONTRACT_CODING_LOCAL"] = "true"
# have to start with this in order to guarantee that app object creation will be in local config.

# also need to start db with pg_ctl -D /usr/local/var/postgres start

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
from testhelperclasses import *
# http://pythonhosted.org/Flask-Testing/
# http://pythontesting.net/framework/unittest/unittest-introduction/

# try to get a file with new test classes

from raceconditiontest import *

gowder_auth = {"Authorization": "Basic Z293ZGVyOnNlY3JldA=="}
# this is the gowder code--- a base64 string of username + : + password I think, judging by this: https://gist.github.com/jarus/1160696 --- gotten by inspecting logged-in request in chrome devtools.



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
        self.assert401(self.client.get("/"))
        self.assert200(self.client.get("/", headers=gowder_auth))
        self.assertEqual(gowder_auth, make_auth_header("gowder", "secret"))
        self.assert401(self.client.get("/admin", headers=make_auth_header("student", "password")))
        self.assert200(self.client.get("/admin", headers=make_auth_header("gowder", "secret")))
        self.assert200(self.client.get("/", headers=make_auth_header("student", "password")))
        self.assertEqual(dbops.list_administrators(), ['gowder'])
        # should add second method for authorized.  also should test auth for admin page with and without admin identity. i.e. need to test that student login can't get admin routes


class TestAddUser(TestStateful):

    def test_add_user(self):
        rsp = self.client.post("/add_user", headers=gowder_auth, data={"lastname": "stub", "email": "none@none.net", "clear_password": "0000"})
        self.assertEqual(rsp.data, b'Successfully added stub!  <a href="/admin">Carry out another admin task?</a>')
        self.assertEqual(dbops.list_users(), ['gowder', 'stub', 'student'])


class TestAddDoc(TestStateful):

    def test_add_document(self):  # should switch to do this from student
        rsp = self.client.post("/enter-data", headers=gowder_auth,
                               data={"1": "no",
                                     "2": "yes",
                                     "3": "no",
                                     "4": "yes",
                                     "5": "no",
                                     "6": "yes",
                                     "7": "no",
                                     "8": "no",
                                     "contract_id": "1"})
        answerlist = dbops.pick_contract(1).answers
        self.assertEqual({answerlist[0].id: answerlist[0].answer,
                          answerlist[1].id: answerlist[1].answer},
                         {1: False, 2: True})
        self.assertEqual(rsp.data, b'To enter another contract, <a href="/">click here!</a>.  If you are done, just close the browser window. <b>Please do not click the link unless you are ready to enter another contract.</b>')
        csvstring = dbops.csv_string()
        with open("test_csv_dump.csv") as cf:
            csvfile = cf.read()
        target_index = csvstring.find("False")  # this allows me to compare the two strings without dealing with the fact that the date and time from the addition above will be different from the known correct data in the file.  I'm basically starting from the first row answers and the whole second row.  So I'm testing that the answer ordering is correct at least.
        self.assertEqual(csvstring[target_index:], csvfile[target_index:])

    def test_caps_addition(self):  # this tests a recurrent bug where capitalized login works but won't let data entry---all usernames are lowercase.
        capitalized_auth_header = make_auth_header("Student", "password")
        rsp = self.client.post("/enter-data", headers=capitalized_auth_header,
                               data={"1": "no",
                                     "2": "yes",
                                     "3": "no",
                                     "4": "yes",
                                     "5": "no",
                                     "6": "yes",
                                     "7": "no",
                                     "8": "no",
                                     "contract_id": "1"})
        answerlist = dbops.pick_contract(1).answers
        self.assertEqual({answerlist[0].id: answerlist[0].answer,
                          answerlist[1].id: answerlist[1].answer},
                         {1: False, 2: True})
        self.assertEqual(rsp.data, b'To enter another contract, <a href="/">click here!</a>.  If you are done, just close the browser window. <b>Please do not click the link unless you are ready to enter another contract.</b>')


class TestChangePassword(TestStateful):
    def test_change_password(self):
        dbops.change_user_password("student", "123456")
        self.assert200(self.client.get("/", headers=make_auth_header("student", "123456")))
        self.assert401(self.client.get("/", headers=make_auth_header("student", "password")))


class TestDatabaseChecks(TestStateful):
    def test_break_database(self):
        db.session.remove()
        db.drop_all()
        self.assertRaises(sqlalchemy.exc.ProgrammingError, dbops.count_contracts)
        db.session.remove()
        db.drop_all()
        db.create_all()
        self.assertEqual(dbops.count_contracts(), 0)
        self.assertEqual(dbops.count_questions(), 0)
        self.assertEqual(len(dbops.list_administrators()), 0)
        cycle()
        self.assertEqual(dbops.count_contracts(), 2)
        self.assertEqual(dbops.count_questions(), 31)
        self.assertEqual(len(dbops.list_administrators()), 1)


class TestFlush(TestStateful):
    def test_mark_live(self):
        self.assertEqual(Contracts.query.get(1).inprogress, False)
        dbops.mark_contract_live(1)
        self.assertEqual(Contracts.query.get(1).inprogress, True)

    def test_flush_contract(self):
        dbops.mark_contract_live(1)
        self.assertEqual(Contracts.query.get(1).inprogress, True)
        sleep(2)
        dbops.flush_documents(seconds=1)
        self.assertEqual(Contracts.query.get(1).inprogress, False)

    def test_force_flush(self):
        dbops.mark_contract_live(1)
        self.assertEqual(Contracts.query.get(1).inprogress, True)
        dbops.force_flush_documents()
        self.assertEqual(Contracts.query.get(1).inprogress, False)

    def test_insufficient_flush_time(self):
        dbops.mark_contract_live(1)
        self.assertEqual(Contracts.query.get(1).inprogress, True)
        dbops.flush_documents()
        self.assertEqual(Contracts.query.get(1).inprogress, True)
        dbops.force_flush_documents()
        self.assertEqual(Contracts.query.get(1).inprogress, False)


class TestEnter(TestStateful):
    def test_list(self):
        dbops.add_answers({1: True, 2: False}, 1, "student")
        dbops.add_answers({1: False, 2: True}, 2, "gowder")
        dbops.add_answers({1: False, 2: True}, 1, "gowder")
        self.assertEqual(len(dbops.get_all_answers()), 6)
        self.assertEqual(dbops.entered_by_counts(), {'gowder': 2, 'student': 1})


class TestModifyQuestion(TestStateful):

    def test_modify_question(self):
        rsp = self.client.post("/add_to_question",
                               headers=make_auth_header("gowder", "secret"),
                               data={"question_id": "1",
                                     "new_exp": "here is some new text"})
        self.assert200(rsp)
        today = str(datetime.date(datetime.now()))
        correct_question = "Is this a contract that purports to change or specify an individual's rights or obligations? \n  ATTENTION: NEW EXPLANATION ADDED on {}, please ensure you've seen it.".format(today)
        correct_explanation = 'Answer "yes" if the document purports to bind an individual to anything, or makes any binding promises or assertions on behalf of the contract author.  In addition to more obvious kinds of promises, this also includes situations, e.g., where the contract says that individuals make representations about their preexisting knowledge or legal rights and obligations (for example, asserting that they own copyright to some content they provide, or that they are knowingly taking some risk). \n\nAnswer "no" if the document is a privacy policy that merely notifies the individual of what will be done with their data, but answer "yes" if there are any other contractual provisions that change a individual\'s legal rights or obligations.  I expect that many privacy policies will be mixed up in here, so please keep an eye out for them.  \n\nYou should also answer "no" if this is an erroneous addition to the dataset, for example, if some random document slipped in.\n\nIf this question is answered "no," coding for this document will terminate.\n\nIn case of doubt, answer "yes." \n added on: {}: here is some new text'.format(today)
        newq = dbops.get_questions()[0]
        self.assertEqual(newq["questiontext"], correct_question)
        self.assertEqual(newq["explanation"], correct_explanation)



if __name__ == '__main__':
    unittest.main()
