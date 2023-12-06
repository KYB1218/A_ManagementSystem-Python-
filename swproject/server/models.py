from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    ID = db.Column(db.String, unique = True, primary_key = True)
    Name = db.Column(db.String)
    PassWd = db.Column(db.String)

    def __init__(self, ID=None, Name=None, PassWd=None):
        self.ID = ID
        self.Name = Name
        self.PassWd = PassWd
    
    def __repr__(self):
        return '<%s,%s,%s>' % (self.ID, self.Name, self.PassWd)

class Equipment(db.Model):
    EquipID = db.Column(db.String, unique = True, primary_key = True)
    EquipName = db.Column(db.String)
    EquipInfo = db.Column(db.String)
    EquipState = db.Column(db.Boolean, default = True)

    def __init__(self, EquipID=None, EquipName = None, EquipInfo = None, EquipState = None):
        self.EquipID = EquipID
        self.EquipName = EquipName
        self.EquipInfo = EquipInfo
        self.EquipState = EquipState

    def __repr__(self):
         return '<%s,%s,%s>' % (self.EquipID, self.EquipName, self.EquipInfo)    

class DeleteLog(db.Model):
    DeleteLogID = db.Column(db.String, primary_key = True, unique = True)
    EquipID = db.Column(db.String, db.ForeignKey('Equipment.EquipID'))
    EquipName = db.Column(db.String, db.ForeignKey('Equipment.EquipName'))
    EquipInfo = db.Column(db.String, db.ForeignKey('Equipment.EquipInfo'))
    EquipState = db.Column(db.Boolean, db.ForeignKey('Equipment.EquipState'))
    ID = db.Column(db.String, db.ForeignKey('User.ID'))
    Name = db.Column(db.String, db.ForeignKey('User.Name'))
    DeletedDate = db.Column(db.Date, default=func.now())

    def __init__ (self, DeleteLogID = None):
        self.DeleteLogID = DeleteLogID
    
    def __repr__(self):
        return '<%s>' % (self.DeleteLogID)
    
class ManageLog(db.Model):
    ManageLogID = db.Column(db.String, primary_key = True, unique = True)
    EquipID = db.Column(db.String, db.ForeignKey('Equipment.EquipID'))
    EquipState = db.Column(db.Boolean, db.ForeignKey('Equipment.EquipState'))
    ID = db.Column(db.String, db.ForeignKey('User.ID'))
    Name = db.Column(db.String, db.ForeignKey('User.Name'))
    ManageLogDate = db.Column(db.Date, default=func.now())

    def __init__ (self, ManageLogID = None):
        self.ManageLogID = ManageLogID

    def __repr__(self):
        return '<%s>' % (self.ManageLogID)