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

class Equipment(db.Model):
    EquipID = db.Column(db.String, unique = True, primary_key = True)
    EquipName = db.Column(db.String)
    EquipInfo = db.Column(db.String)
    EquipState = db.Column(db.String)

    def __init__(self, EquipID=None, EquipName = None, EquipInfo = None, EquipState = None):
        self.EquipID = EquipID
        self.EquipName = EquipName
        self.EquipInfo = EquipInfo
        self.EquipState = EquipState

class DeleteLog(db.Model):
    DeleteLogID = db.Column(db.Integer, primary_key = True, unique = True, autoincrement=True)
    DeletedEquipID = db.Column(db.String)
    DeletedEquipName = db.Column(db.String)
    DeletedEquipInfo = db.Column(db.String)
    DeletedEquipState = db.Column(db.String)
    DeleterID = db.Column(db.String)
    DeleterName = db.Column(db.String)
    DeletedDate = db.Column(db.Integer)

    def __init__ (self, DeleteLogID, DeletedEquipID, DeletedEquipName, DeletedEquipInfo,
                  DeletedEquipState, DeletedDate, DeleterID, DeleterName):
        self.DeleteLogID = DeleteLogID
        self.DeletedEquipID = DeletedEquipID
        self.DeletedEquipName = DeletedEquipName
        self.DeletedEquipInfo = DeletedEquipInfo
        self.DeletedEquipState = DeletedEquipState
        self.DeleterID = DeleterID
        self.DeleterName = DeleterName
        self.DeletedDate = DeletedDate
    
class ManageLog(db.Model):
    ManageLogID = db.Column(db.String, primary_key = True, unique = True, autoincrement=True)
    UsedEquipID = db.Column(db.String)
    UsedEquipState = db.Column(db.String)
    UserID = db.Column(db.String)
    UserName = db.Column(db.String)
    ManageLogDate = db.Column(db.Integer)

    def __init__ (self, ManageLogID, UsedEquipID, UsedEquipState, UserID, UserName, ManageLogDate):
        self.ManageLogID = ManageLogID
        self.UsedEquipID = UsedEquipID
        self.UsedEquipState = UsedEquipState
        self.UserID = UserID
        self.UserName = UserName
        self.ManageLogDate = ManageLogDate