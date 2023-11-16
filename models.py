from server import db

class user(db.Model):
    id = db.Column(db.Integer, unique = True)
    name = db.Column(db.String)
    userNFC = db.Column(db.Integer, primary_key = True)

    def __init__(self, id=1, name=None, userNFC=1):
        self.id = id
        self.name = name
        self.userNFC = userNFC
    
    def __repr__(self):
        return '<%r>' % (self.name)