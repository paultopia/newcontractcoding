from core import db
db.session.remove()
db.drop_all()
