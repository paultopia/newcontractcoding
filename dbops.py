import bcrypt
import csv
import os
from core import db
from database import Contracts, Questions, Users, Answers
from datetime import datetime
from io import StringIO


# I should just make an admin view with an interface to add other users, and to grab the documents to code from a url somewhere.


###########################
#
# USERS
#
###########################

def make_password_hash(clear_password):
    return bcrypt.hashpw(clear_password.encode('utf8'), bcrypt.gensalt()).decode('utf8')


def add_user(lastname, email, clear_password, isadmin=False):
    hashed_password = make_password_hash(clear_password)
    user = Users(lastname.lower(), email, hashed_password, isadmin)
    db.session.add(user)
    db.session.commit()
    return lastname


def change_user_password(lastname, new_password):
    user = Users.query.get(lastname.lower())
    if user:
        hashed_password = make_password_hash(new_password)
        user.password = hashed_password
        db.session.commit()
        return True
    return False
# this is mainly for myself: I can add a dummy password for myself and then immediately login (USING INCOGNITO SO IT DOESN'T GET CACHED) and change it.


def list_users():
    return [x.lastname for x in Users.query.order_by(Users.lastname).all()]


def list_administrators():
    return [x.lastname for x in Users.query.filter_by(isadmin=True).all()]


def is_admin(lastname):
    return Users.query.get(lastname.lower()).isadmin


def find_hashed_password(lastname):
    return Users.query.get(lastname.lower()).password


def add_users(usersjson):
    users = [Users(x["lastname"].lower(),
                   x["email"],
                   bcrypt.hashpw(x["password"].encode('utf8'), bcrypt.gensalt()).decode('utf8'),
                   x["isadmin"]) for x in usersjson]
    db.session.add_all(users)
    db.session.commit()
    return True

###########################
#
# QUESTIONS
#
###########################


def get_questions():
    return [{"question_id": str(x.id),
             "questiontext": x.questiontext,
             "explanation": x.explanation} for x in Questions.query.order_by(Questions.id).all()]


def add_questions(questionsjson):
    questions = [Questions(x["text"], x["explanation"]) for x in questionsjson]
    db.session.add_all(questions)
    db.session.commit()
    return True

###########################
#
# CONTRACTS
#
###########################


def mark_contract_live(contract_id):
    contract = Contracts.query.get(contract_id)
    contract.inprogress = True
    contract.inprogressstarted = datetime.utcnow()
    db.session.commit()
    return contract_id


def mark_contract_entered(contract_id, user_name):
    """mark document as entered.

    if document already has a first entry, then add a second entry.
    if not, add a first entry.  Also flip state from live to not-live.
    """
    contract = Contracts.query.get(contract_id)
    if contract.firstenteredby:
        contract.secondenteredby = user_name
        contract.secondenteredon = datetime.utcnow()
    else:
        contract.firstenteredby = user_name
        contract.firstenteredon = datetime.utcnow()
    contract.inprogress = False
    db.session.commit()
    return contract_id


def fetch_contract(user_name):
    """select a document to code

    First look for documents that aren't entered at all, and select the first one.
    If there are no documents that aren't entered, then look for documents only entered once.

    for second coding, only query on docs not coded by this user for first coding.

    If there are no docs for this user to second-do as well, ask them to wait and talk to me.

    Ignore documents marked as in progress.

    returns contract id and text + userid just in case.
    """
    contract = Contracts.query.filter_by(inprogress=False, firstenteredby=None).first()
    if contract is None:
        contract = Contracts.query.filter(Contracts.firstenteredby != user_name).filter_by(inprogress=False, secondenteredby=None).first()
        if contract is None:
            # TODO: trigger some kind of log or other notification to me that this user doesn't have anything to do.  then I can go in and flush in progress, nag other people to catch up, etc.
            return None
    mark_contract_live(contract.id)
    return {"contract_id": str(contract.id), "contract_url": contract.url, "contract_text": contract.contract, "user_name": user_name}


def hours_ago(now, then):
    diff = now - then
    return diff.total_seconds() / 3600.0


def is_stale(contract_row):
    now = datetime.utcnow()
    diff = hours_ago(now, contract_row.inprogressstarted) # may fail if inprogressstarted needs to be parsed to get a datetime object.
    return diff > 1


def flush_documents():
    """get every doc that has been marked as live for > 1hr and mark it non-live
    
    I'm a little bit concerned about this: if there are a lot of stale documents, this could blow out the memory.  
    Could I keep them out of memory by doing the update in the database layer inside the query object?  I'm not sure.
    Need to find out: 
    (a) whether some update like 2/3 in here https://stackoverflow.com/a/33638391/4386239 that doesn't actually fetch docs will keep the records out of memory in the python application, 
    (b) if so, whether that will mean that heroku will let me run it off-dyno w/o memory limits, since postgres is all kinds of separate process, and 
    (c) if so, how to actually execute the time diff check query inside the ORM rather than in python code.
    
    But that might also be a premature optimization, since this is an unlikely corner case---worst case scenario I blow the memory and then I just manually update every record to turn off inprogress flag and restart. 
    """
    contracts = Contracts.query.filter_by(inprogress=True).all()
    stale = filter(is_stale, contracts)
    for k in stale:
        k.inprogress = False
    db.session.commit()
    return True


def force_flush_documents():
    """flush all contracts, regardless of time"""
    contracts = Contracts.query.order_by(Contracts.id).all()
    for k in contracts:
        k.inprogress = False
    db.session.commit()
    return True


def add_contract(contract_as_dict):
    k = Contracts(contract_as_dict["contract"], contract_as_dict["url"], str(datetime.utcnow()), "admin")
    db.session.add(k)
    db.session.commit()
    return True


def add_contracts(contractsjson):
    contracts = [Contracts(x["contract"], x["url"], x["firstadded"], x["firstaddedby"]) for x in contractsjson]
    db.session.add_all(contracts)
    db.session.commit()
    return True

###########################
#
# ANSWERS
#
###########################


def add_answers(answers_from_user, contract_id, user_name):
    """expect answers_from_user to be a dict of {question_id: choice}
    but may have to massage types to get them in; type massaging will happen
    in a view function somewhere before it's passed in here (e.g. converting ids
    from strings to integers)"""
    answers = [Answers(x, contract_id, answers_from_user[x], user_name) for x in answers_from_user.keys()]
    db.session.add_all(answers)
    db.session.commit()
    mark_contract_entered(contract_id, user_name)  # this includes a redundant db commit
    return contract_id

###########################
#
# HELPER CODE FOR TESTING/DEBUGGING
#
###########################


def get_all_answers():
    return Answers.query.order_by(Answers.id).all()


def pick_contract(contract_id):
    return Contracts.query.get(contract_id)


###########################
#
# CSV FORMAT DATA OUTPUT
#
###########################

# all this stuff needs testing especially on the ordering stuff, with a full pile of data so I don't blow it up

def _header_row():
    questions = [x.questiontext for x in Questions.query.order_by(Questions.id).all()]
    kcols = ["contract", "url", "firstadded", "firstaddedby", "firstenteredby", "firstenteredon", "secondenteredby", "secondenteredon"]
    return kcols + questions


def _contract_row(contract_id):
    contract = pick_contract(contract_id)
    kfields = [contract.contract, contract.url, contract.firstadded, contract.firstaddedby, contract.firstenteredon, contract.secondenteredby, contract.secondenteredon]
    answers = [x.answer for x in sorted(contract.answers, key=lambda y: y.question)]
    return kfields + answers


def _build_csv(filelike): 
    rows = Contracts.query.count()
    writer = csv.writer(filelike, lineterminator='\n')
    writer.writerow(_header_row())
    for contract_id in range(1, rows + 1):
        writer.writerow(_contract_row(contract_id))
    return None
    
def csv_file(full_path_to_file):
    dir = os.path.dirname(full_path_to_file)
    if not os.path.exists (dir):
        os.makedirs(dir)  
        # this has a race condition, but I don't care, since I'll be the only one getting this and there's only one of me. Mitigtation strategy if I start to care suggested here: https://stackoverflow.com/questions/273192/how-can-i-create-a-directory-if-it-does-not-exist
    with open(full_path_to_file, 'w') as out:  # overwriting but don't care.
        _build_csv(out)
    return full_path_to_file

    
def csv_string():
    with StringIO() as out:
        _build_csv(out)
        return out.getvalue()
