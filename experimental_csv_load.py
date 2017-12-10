import requests
from core import db
from database import Contracts
from contextlib import closing
import csv
import codecs
db.create_all()
url = "http://localhost:8000/csv-test-data.csv"  # serving with SimpleHTTPServer


def add_row_to_db(row):
    contract = row[1]
    url = row[2]
    fad = row[3]
    fab = row[4]
    k = Contracts(contract, url, fad, fab)
    db.session.add(k)
    db.session.commit()


with closing(requests.get(url, stream=True)) as r:
    reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'), delimiter=',')
    for row in reader:
        add_row_to_db(row)
        print(row)

# I'm not sure if this will work with quoted/escaped/multiline text.  I got the technique from here https://stackoverflow.com/a/38677650/4386239 that added a quotechar.

# however, with my simple test data this works to stream-add data from csv url formatted like csv-test-data.csv in repo.

# would still be nicer to do it in psql if possible, tracking this SO I posted to see if there's a way https://stackoverflow.com/questions/47736253/add-data-to-postgres-from-csv-then-continue-primary-key-from-that-number-for-pro
