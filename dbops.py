from core import db
from database import Contracts, Questions, Users, Answers
from datetime import datetime


def add_answer(question_id, contract_id, choice, user_id):
    answer = Answers(question_id, contract_id, choice, user_id)
    db.session.add(answer)
    db.session.commit()
    return question_id, contract_id


def bulk_add_answers(answers_from_user, contract_id, user_id):
    """expect answers_from_user to be a dict of {question_id: choice}
    but may have to massage types to get them in; type massaging will happen
    in a view function somewhere before it's passed in here (e.g. converting ids
    from strings to integers)"""
    answers = [Answers(x, contract_id, answers_from_user[x], user_id) for x in answers_from_user.keys()]
    db.session.add_all(answers)
    db.session.commit()
    return contract_id


def make_contract_live(contract_id):
    contract = Contracts.query.get(contract_id)
    contract.inprogress = True
    contract.inprogressstarted = datetime.utcnow()
    db.session.commit()
    return contract_id


def mark_contract_entered(contract_id, user_id):
    """mark document as entered.

    if document already has a first entry, then add a second entry.
    if not, add a first entry.  Also flip state from live to not-live.
    """
    contract = Contracts.query.get(contract_id)
    if contract.firstenteredby:
        contract.secondenteredby = user_id
        contract.secondenteredon = datetime.utcnow()
    else:
        contract.firstenteredby = user_id
        contract.secondenteredby = datetime.utcnow()
    contract.inprogress = False
    db.session.commit()
    return contract_id


def serve_document(user_id):
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
        contract = Contracts.query.filter(Contracts.name != user_id).filter_by(inprogress=False, secondenteredby=None).first()
        if contract is None:
            # TODO: trigger some kind of log or other notification to me that this user doesn't have anything to do.  then I can go in and flush in progress, nag other people to catch up, etc.
            return None
    make_contract_live(contract.id)
    return {"contract_id": contract.id, "contract_text": contract.contract, "user_id": user_id}


def flush_documents():
    """get every doc that has been marked as live for > 1hr and mark it non-live"""
    pass  # TODO
