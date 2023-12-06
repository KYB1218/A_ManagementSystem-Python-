import pandas as pd
import json
import sqlite3
from datetime import datetime

from flask import request
from flask_restx import Resource, Api, Namespace, fields
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

import models

db = SQLAlchemy()  # app.py에서 sqlalchemy 호출시 순환 호출 오류 발생하여 각 api마다 호출

Equipment = Namespace("Equipment", description="Equipment DB(기자재의 정보를 저장하는 DB)와 통신하는 Api")

parser = Equipment.parser()  # 헤더를 추가하기 위한 변수
parser.add_argument("Authorization", location="headers")  # 헤더를 입력받기 위해 기대 입력값을 추가

EquipField = Equipment.model(
    "Equipment",
    {
        "EquipID": fields.String(description = "기자재 ID"),
        "EquipName": fields.String(description = "기자재 이름"),
        "EquipInfo": fields.String(description = "상세정보"),
        "EquipState": fields.String(description="대여 상태", default="대여 가능")
    },
)

#기자재 추가
@Equipment.route("",methods=['GET', 'POST'])
class EquipmentAdd(Resource):
    @Equipment.expect(EquipField)
    @Equipment.expect(parser)
    def post(self):
        """Equipment의 정보를 저장하는 API\n
        기자재의 ID, 이름, 상세정보, 대여 상태를 json의 형태로 전달받아 DB에 저장한다."""

        #데이터 입력값으로부터 가져오기
        EquipID = request.json.get("EquipID")
        EquipName = request.json.get("EquipName")
        EquipInfo = request.json.get("EquipInfo")
        try:
            EquipState = int(request.json.get("EquipState"))
        except ValueError:
            return "EquipState should be int."
        
        Equip_data = models.Equipment(EquipID=EquipID, EquipName=EquipName, EquipInfo=EquipInfo, EquipState=EquipState)
        db.session.add(Equip_data)

        try:
            db.session.commit()
            db.session.flush()
        except:
            db.session.rollback()

            return "This Equipment already exist."
        return 0

#기자재 목록    
@Equipment.route("/EquipList")
class EquipmentList(Resource):
       @jwt_required()
       @Equipment.expect(parser)
       def get(self):
        """Equipment 목록을 반환하는 API"""

        equipment_list = []
        equipments = db.session.query(models.Equipment).all()

        for equipment in equipments:
            equipment_data = {
                "EquipID": equipment.EquipID,
                "EquipName": equipment.EquipName,
                "EquipInfo": equipment.EquipInfo,
                "EquipState": equipment.EquipState
            }
            equipment_list.append(equipment_data)

        return equipment_list

# 기자재 삭제 후 삭제 정보들 DeleteLog에 추가
@Equipment.route("/EquipDel/<EID>")
class EquipDelete(Resource):
    @Equipment.expect(parser)
    @jwt_required()
    def delete(self, EID):
        """Equipment 정보를 삭제하는 API\n
        ID를 입력받아 해당 ID와 동일한 Equipment 정보를 삭제한다.\n
        jwt 인증의 경우 헤더에 Authorization: Bearer jwt를 입력하여야 한다."""

        current_user_id = get_jwt_identity()
        equipment = db.session.query(models.Equipment).filter(models.Equipment.EquipID == EID).first()
        if equipment:
            # 사용자 정보 가져오기 - 예시로 User 모델에서 가져온다고 가정
            current_user = models.User.query.filter_by(ID=current_user_id).first()

            delete_log_length = len(models.DeleteLog.query.all())

            # DeleteLog에 로그 추가
            DeleteLog = models.DeleteLog(DeleteLogID = delete_log_length + 1, DeletedEquipID = equipment.EquipID, DeletedEquipName = equipment.EquipName,
                                          DeletedEquipInfo = equipment.EquipInfo, DeletedEquipState=equipment.EquipState, 
                                          DeleterID = current_user.ID, DeleterName = current_user.Name, DeletedDate=datetime.utcnow())
            db.session.add(DeleteLog)

            # 기자재 삭제
            db.session.delete(equipment)
            db.session.commit()
            return f"Equipment {EID} deleted successfully."
        else:
            return f"Equipment {EID} not found."
        
#기자재 대여/반납
@Equipment.route("/EquipManager/<EID>")
class EquipManage(Resource):
    @Equipment.expect(parser)
    @jwt_required()
    def put(self, EID):
        """Equipment 상태를 변경하는 API\n
        ID를 입력받아 해당 ID의 Equipment 상태를 변경한다.\n
        jwt 인증의 경우 헤더에 Authorization: Bearer jwt를 입력하여야 한다."""

        current_user_id = get_jwt_identity()
        equipment = db.session.query(models.Equipment).filter(models.Equipment.EquipID == EID).first()

        if equipment:
            # 사용자 정보 가져오기
            current_user = models.User.query.filter_by(ID=current_user_id).first()

            # 새로운 상태 결정
            if equipment.EquipState == "대여 가능":
                new_state = "대여"

            # 상태 변경 전 상태 로그 추가
            manage_log_length = len(models.ManageLog.query.all())

            manage_log = models.ManageLog(ManageLogID=manage_log_length + 1, EquipID=equipment.EquipID,
                                          UsedEquipState=new_state, UserID=current_user.ID, UserName=current_user.Name,
                                          ManageLogDate=datetime.utcnow())
            db.session.add(manage_log)

            # 상태 변경
            equipment.EquipState = new_state
            db.session.commit()
            return f"Equipment {EID} state changed to {new_state} successfully."
        else:
            return f"Equipment {EID} not found."
