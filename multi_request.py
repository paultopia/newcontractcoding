"""
test file to run after spinning up gunicorn app:app -w=2
"""


import requests, concurrent.futures, re

import os
os.environ["NEW_CONTRACT_CODING_LOCAL"] = "true"
from core import db
import dbops

def make_dummy_contracts():
    out = []
    for x in range(1000):
        out.append({"contract": "This is contract number " + str(x),
                    "url": "http://foo",
                    "firstadded": "cat",
                    "firstaddedby": "meow"})
    return out

regex = re.compile(r'contract number (\d*)')

def test_document_correctness(doclist, rightnum):
    docnumbers = [int(re.findall(regex, item.text)[0]) for item in doclist]
    assert(len(set(docnumbers)) == rightnum)

def test_setup():
    db.create_all()
    from json import load
    dbops.add_contracts(make_dummy_contracts())
    with open("testusers.json") as tu:
        dbops.add_users(load(tu))
    with open("testquestions.json") as tq:
        dbops.add_questions(load(tq))
    print("setup complete")


def teardown():
    db.session.remove()
    db.drop_all()
    print("database beaten up")

gowder_auth = {"Authorization": "Basic Z293ZGVyOnNlY3JldA=="}

def firstcontract(response):
    return "contract number 0" in response.text

def secondcontract(response):
    return "contract number 1" in response.text


def gimme(_=None):
    return requests.get("http://127.0.0.1:8000/", headers=gowder_auth)

def test_the_things_sync(numcalls):
    teardown()
    test_setup()
    print("starting requests")
    results = [gimme() for x in range(numcalls)]
    print("testing the thing sync")
    test_document_correctness(results, numcalls)
    print("I ran, really, I did.  sync.")

#test_the_things_sync(10)


def test_regex():
    print(re.findall(regex, "this is contract number 55"))


def test_the_things_async(numcalls):
    teardown()
    test_setup()
    #results = []
    print("testing the thing async")
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=32)
    calls = pool.map(gimme, range(numcalls))
    test_document_correctness(list(calls), numcalls)
    print("I tested the thing, async, yo")

test_the_things_async(100)
