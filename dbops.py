from core import db
from database import Contracts, Questions, Users, Answers
from datetime import datetime

def add_answer():
    pass


def make_document_live(docid):
    contract = Contracts.query.get(docid)
    contract.inprogress = True
    contract.inprogressstarted = datetime.utcnow()
    db.session.commit()
    return docid


def mark_document_entered(docid):
    """mark document as entered.

    if document already has a first entry, then add a second entry.
    if not, add a first entry.  Also flip state from live to not-live.
    """
    pass


def serve_document(userid):
    """select a document to code

    First look for documents that aren't entered at all, and select the first one.
    If there are no documents that aren't entered, then look for documents only entered once.

    for second coding, only query on docs not coded by this user for first coding.

    If all documents are entered twice, report that we're done.

    Ignore documents marked as in progress.  But if any documents are marked as in progress and there are no other un-entered documents, trigger a flush then re-query.

    If flush and requery per prev branch yields nothing, ask user to wait.
    """
    pass


def flush_documents():
    """get every doc that has been marked as live for > 1hr and mark it non-live"""
    pass