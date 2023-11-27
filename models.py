from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class user(db.Model):
    __tablename__ = 'user'
    userID = db.Column(db.Integer, unique = True, primary_key = True)
    userName = db.Column(db.String)
    userBirth = db.Column(db.Date)
    userPW = db.Column(db.String)

    def __init__(self, userID=None, userName=None, userBirth=None, userPW=None):
        self.userID = userID
        self.userName = userName
        self.userBirth = userBirth
        self.userPW = userPW
    
    def __repr__(self):
        return '<%s,%s,%s>' % (self.userID, self.userName, self.userPW)

class equipment(db.Model):
    __tablename__ = 'equipment'
    equipmentID = db.Column(db.String, unique = True, primary_key = True)
    equipmentName = db.Column(db.String)
    equipmentInfo = db.Column(db.String)
    state = db.Column(db.Boolean, default = True)

    def __init__(self, equipmentID=None, equipmentName = None, equipmentInfo = None, state = None):
        self.equipmentID = equipmentID
        self.equipmentName = equipmentName
        self.equipmentInfo = equipmentInfo
        self.state = state

    def __repr__(self):
         return '<%s,%s,%s>' % (self.equipmentID, self.equipmentName, self.equipmentInfo)    

class deleteLog(db.Model):
    __tablename__ = 'deleteLog'
    deleteLogID = db.Column(db.String, primary_key = True, unique = True)
    deletedID = db.Column(db.String, db.ForeignKey('equipment.equipmentID'))
    deletedName = db.Column(db.String, db.ForeignKey('equipment.equipmentName'))
    deletedInfo = db.Column(db.String, db.ForeignKey('equipment.equipmentInfo'))
    deletedState = db.Column(db.Boolean, db.ForeignKey('equipment.state'))
    deleterId = db.Column(db.String, db.ForeignKey('user.userID'))
    deleterName = db.Column(db.String, db.ForeignKey('user.userName'))
    deleteDate = db.Column(db.Date, default=func.now())

    def __init__ (self, deleteLogID = None):
        self.deleteLogID = deleteLogID
    
    def __repr__(self):
        return '<%s>' % (self.deleteLogID)
    
class manageLog(db.Model):
    __tablename__ = 'manageLog'
    manageLogID = db.Column(db.String, primary_key = True, unique = True)
    usedEquipID = db.Column(db.String, db.ForeignKey('equipment.equipmentID'))
    usedState = db.Column(db.Boolean, db.ForeignKey('equipment.state'))
    managerID = db.Column(db.String, db.ForeignKey('user.userID'))
    managerName = db.Column(db.String, db.ForeignKey('user.userName'))
    logDate = db.Column(db.Date, default=func.now())

    def __init__ (self, manageLogID = None):
        self.manageLogID = manageLogID

    def __repr__(self):
        return '<%s>' % (self.manageLogID)