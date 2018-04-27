from core import db
from database import Contracts, Answers
from datetime import datetime

def safer_add_answers(answers_from_user, contract_id, user_name):
    """expect answers_from_user to be a dict of {question_id: choice}
    
    this new version of add_answers will make sure that the contract gets marked correctly as updated 
    before returning, and inform caller accordingly, so that view function calling it can decide 
    whether or not to show a new page depending on success.
    """
    uname = user_name.lower()
    whichentry = 0
    now = datetime.utcnow()
    contract = Contracts.query.get(contract_id)
    if contract.firstenteredby:
        contract.secondenteredby = uname
        contract.secondenteredon = now
        whichentry = 1
    else:
        contract.firstenteredby = uname
        contract.firstenteredon = now
        whichentry = 2
    contract.inprogress = False
    answers = [Answers(x, contract_id, answers_from_user[x], uname) for x in answers_from_user.keys()]
    db.session.add_all(answers)
    db.session.commit()
    updated_contract = Contracts.query.get(contract_id)
    errorstate = True
    if whichentry == 1 and updated_contract.firstenteredby == uname and updated_contract.inprogress == False:
    	errorstate = False
    elif whichentry == 2 and updated_contract.secondenteredby == uname and updated_contract.inprogress == False:
    	errorstate = False
    return {"id": contract_id, "error": errorstate}
