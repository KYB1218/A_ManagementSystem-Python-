import pandas as pd
import json
import sqlite3

from flask import request
from flask_restx import Resource, Api, Namespace, fields
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import jwt_required

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
        "EquipState": fields.Boolean(description="대여 상태", default=True)
    },
)

#기자재 추가
@Equipment.route("",methods=['GET', 'POST'])
class EquipmentAdd(Resource):
    @Equipment.expect(parser)
    @Equipment.expect(EquipField)
    def post(self):
        """Equipment의 정보를 저장하는 API\n
        기자재의 ID, 이름, 상세정보, 대여 상태를 json의 형태로 전달받아 DB에 저장한다."""

        #데이터 입력값으로부터 가져오기
        EquipID = request.json.get("EquipID")
        EquipName = request.json.get("EquipName")
        EquipInfo = request.json.get("EquipInfo")
        try:
            EquipState = bool(request.json.get("EquipState"))
        except ValueError:
            return "EquipState should be boolean."
        
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

#기자재 검색    
@Equipment.route("/<EID>")
class EquipEdit(Resource):
    @jwt_required()
    @Equipment.expect(parser)
    def get(self, EID):
        """Equipment의 정보를 가져오는 API\n
        ID를 입력받아 해당 ID와 동일한 Equipment의 이름, 상세정보, 대여상태를 반환한다.\n
        jwt 인증의 경우 헤더에 Authorization: Bearer jwt를 입력하여야 한다."""
    
        data = db.session.query(models.Equipment).filter(models.Equipment.EquipID.like(EID)).first()

        try:
            return {"EquipID": data.EquipID, "EquipName": data.EquipName, "EquipInfo": data.EquipInfo, "EquipState": data.EquipState}
        except AttributeError:
            return "This Equipment doesn't exist"

#기자재 삭제        
@Equipment.route("/EquipDelete/<EID>")
class EquipDelete(Resource):
    @jwt_required()
    @Equipment.expect(parser)
    def delete(self, EID):
        """Equipment 정보를 삭제하는 API\n
        ID를 입력받아 해당 ID와 동일한 Equipment 정보를 삭제한다.\n
        jwt 인증의 경우 헤더에 Authorization: Bearer jwt를 입력하여야 한다."""

        equipment = db.session.query(models.Equipment).filter(models.Equipment.EquipID == EID).first()
        if equipment:
            db.session.delete(equipment)
            db.session.commit()
            return f"Equipment {EID} deleted successfully."
        else:
            return f"Equipment {EID} not found."

# #기자재 목록    
# @Equipment.route("/EquipList")
# class EquipmentList(Resource):
#     @jwt_required()
#     @Equipment.expect(parser)
#     def get(self):
#         """Equipment 목록을 반환하는 API"""

#         equipment_list = []
#         equipments = db.session.query(models.Equipment).all()

#         for equipment in equipments:
#             # 각 기자재에 대한 정보와 상태 변경을 위한 버튼 정보를 추가
#             equipment_data = {
#                 "EquipID": equipment.EquipID,
#                 "EquipName": equipment.EquipName,
#                 "EquipInfo": equipment.EquipInfo,
#                 "EquipState": equipment.EquipState,
#                 "ChangeStateURL": f"/api/Equipment/ChangeState/{equipment.EquipID}"  # 상태 변경을 위한 API URL
#             }
#             equipment_list.append(equipment_data)

#         return equipment_list
