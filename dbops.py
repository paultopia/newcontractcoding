import bcrypt
from core import db
from database import Contracts, Questions, Users, Answers
from datetime import datetime


# I should just make an admin view with an interface to add other users, and to grab the documents to code from a url somewhere.


###########################
#
# USERS
#
###########################


def add_user(lastname, email, clear_password, isadmin=False):
    hashed_password = bcrypt.hashpw(clear_password, bcrypt.gensalt())
    user = Users(lastname, email, hashed_password, isadmin)
    db.session.add(user)
    db.session.commit()
    return lastname


def list_users():
    return [x.lastname for x in Users.query(Users.lastname).all()]


def is_admin(lastname):
    return Users.query.get(lastname).isadmin


def find_hashed_password(username):
    return Users.query.filter_by(lastname=username).first().password


def add_users(usersjson):
    users = [Users(x["lastname"],
                   x["email"],
                   bcrypt.hashpw(x["password"], bcrypt.gensalt()),
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
    return [{"question_id": str(question.id),
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
        contract.secondenteredby = datetime.utcnow()
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
        contract = Contracts.query.filter(Contracts.name != user_name).filter_by(inprogress=False, secondenteredby=None).first()
        if contract is None:
            # TODO: trigger some kind of log or other notification to me that this user doesn't have anything to do.  then I can go in and flush in progress, nag other people to catch up, etc.
            return None
    mark_contract_live(contract.id)
    return {"contract_id": str(contract.id), "contract_text": contract.contract, "user_name": user_name}


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
