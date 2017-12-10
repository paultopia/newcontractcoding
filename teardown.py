from core import db
db.session.remove()
db.drop_all()
print("torn down!")
