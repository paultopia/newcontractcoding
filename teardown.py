import os
os.environ["NEW_CONTRACT_CODING_LOCAL"] = "true"
from core import db
db.session.remove()
db.drop_all()
print("torn down!")
