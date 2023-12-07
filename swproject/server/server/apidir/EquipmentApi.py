import pandas as pd
import json
import sqlite3
from datetime import datetime

from flask import request
from flask_restx import Resource, Api, Namespace, fields
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func

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
        EquipState = request.json.get("EquipState")
        
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
        now = datetime.utcnow()
        formatted_date = int(now.strftime("%Y%m%d"))

        if equipment:
            # 사용자 정보 가져오기
            current_user = models.User.query.filter_by(ID=current_user_id).first()

            latest_delete_log = db.session.query(func.max(models.DeleteLog.DeleteLogID)).scalar()
            if latest_delete_log is not None:
                delete_log_id = latest_delete_log + 1
            else:
                delete_log_id = 1

            # DeleteLog에 로그 추가
            DeleteLog = models.DeleteLog(DeleteLogID = delete_log_id, DeletedEquipID = equipment.EquipID, DeletedEquipName = equipment.EquipName,
                                          DeletedEquipInfo = equipment.EquipInfo, DeletedEquipState=equipment.EquipState, 
                                          DeleterID = current_user.ID, DeleterName = current_user.Name, DeletedDate=formatted_date)
            db.session.add(DeleteLog)

            # 기자재 삭제
            db.session.delete(equipment)
            db.session.commit()
            return f"Equipment {EID} deleted successfully."
        else:
            return f"Equipment {EID} not found."
        
#기자재 대여
@Equipment.route("/EquipRental/<EID>")
class EquipRental(Resource):
    @Equipment.expect(parser)
    @jwt_required()
    def put(self, EID):
        """기자재를 대여하는 API\n
        기자재 ID를 입력받아 해당 ID의 Equipment 대여 중 상태로 변환한다.\n
        jwt 인증의 경우 헤더에 Authorization: Bearer jwt를 입력하여야 한다."""

        current_user_id = get_jwt_identity()
        equipment = db.session.query(models.Equipment).filter(models.Equipment.EquipID == EID).first()
        manage = db.session.query(models.ManageLog).filter(models.ManageLog.UsedEquipID == EID).first()
        now = datetime.utcnow()
        formatted_date = int(now.strftime("%Y%m%d"))

        if equipment:
            # 사용자 정보 가져오기
            current_user = models.User.query.filter_by(ID=current_user_id).first()

            latest_manage_log = db.session.query(func.max(models.ManageLog.ManageLogID)).scalar()
            if latest_manage_log is not None:
                manage_log_id = latest_manage_log + 1
            else:
                manage_log_id = 1
            
            # 새로운 상태 결정
            if equipment.EquipState == "대여 가능":
                new_state = "대여"

                manage_log = models.ManageLog(ManageLogID=manage_log_id, UsedEquipID=equipment.EquipID,
                                              UsedEquipState=new_state, UserID=current_user.ID, UserName=current_user.Name,
                                              ManageLogDate=formatted_date)
                db.session.add(manage_log)
                equipment.EquipState = "대여 중"
                db.session.commit()

            elif equipment.EquipState == "대여 중" and current_user.ID == manage.UserID:
                return "이미 대여한 기자재입니다."
            
            else:
                return f"대여 불가능"

            return f"Equipment {EID} state changed to {new_state} successfully."
        else:
            return f"Equipment {EID} not found."

#기자재 반납
@Equipment.route("/EquipBack/<EID>")
class EquipBack(Resource):
    @Equipment.expect(parser)
    @jwt_required()
    def put(self, EID):
        """기자재를 반납하는 API\n
        ID를 입력받아 해당 ID의 Equipment 상태를 변경한다.\n
        jwt 인증의 경우 헤더에 Authorization: Bearer jwt를 입력하여야 한다."""

        current_user_id = get_jwt_identity()
        equipment = db.session.query(models.Equipment).filter(models.Equipment.EquipID == EID).first()
        manage = db.session.query(models.ManageLog).filter(models.ManageLog.UsedEquipID == EID).first()
        now = datetime.utcnow()
        formatted_date = int(now.strftime("%Y%m%d"))

        if equipment:
            # 사용자 정보 가져오기
            current_user = models.User.query.filter_by(ID=current_user_id).first()

            latest_manage_log = db.session.query(func.max(models.ManageLog.ManageLogID)).scalar()
            if latest_manage_log is not None:
                manage_log_id = latest_manage_log + 1
            else:
                manage_log_id = 1

            # 새로운 상태 결정
            if equipment.EquipState == "대여 중" and manage.UserID == current_user.ID:
                new_state = "반납"

                manage_log = models.ManageLog(ManageLogID=manage_log_id, UsedEquipID=equipment.EquipID,
                                              UsedEquipState=new_state, UserID=current_user.ID, UserName=current_user.Name,
                                              ManageLogDate=formatted_date)
                db.session.add(manage_log)
                equipment.EquipState = "대여 가능"
                db.session.commit()

            elif equipment.EquipState == "대여 중" and manage.UserID != current_user.ID:
                return "대여한 기자재가 아닙니다."

            return f"Equipment {EID} state changed to {new_state} successfully."
        else:
            return f"Equipment {EID} not found."

#가장 최근에 대여한 사용자 이름 띄우기
@Equipment.route("/RecentRentalUser/<EID>")
class RecentRentalUser(Resource):
    @Equipment.expect(parser)
    @jwt_required()
    def get(self, EID):
        """특정 기자재를 최근에 대여한 사용자의 이름을 반환하는 API"""

        # 특정 기자재의 최근 대여 로그를 가져오기
        recent_rental_log = db.session.query(models.ManageLog).filter(
            models.ManageLog.UsedEquipID == EID,
            models.ManageLog.UsedEquipState == '대여'
        ).order_by(models.ManageLog.ManageLogID.desc()).first()

        if recent_rental_log:
            # 최근에 대여한 사용자의 정보 가져오기
            recent_user = models.User.query.filter_by(ID=recent_rental_log.UserID).first()

            if recent_user:
                return {"RecentRentalUserName": recent_user.Name}
            else:
                return "사용자 정보를 찾을 수 없습니다."
        else:
            return "해당 기자재가 대여 중이 아닙니다."
        
#마이페이지 (내가 지금 빌리고 있는 물건들 목록화)
from sqlalchemy import or_

@Equipment.route("/UserCurrentRentals")
class UserCurrentRentals(Resource):
    @jwt_required()
    @Equipment.expect(parser)
    def get(self):
        """로그인한 사용자가 현재 빌리고 있는 물건들의 정보를 반환하는 API"""
        current_user_id = get_jwt_identity()
        
        # 사용자가 현재 대여중인 EquipID 목록 가져오기
        user_current_rentals = db.session.query(models.ManageLog).filter(
            models.ManageLog.UserID == current_user_id,
            models.ManageLog.UsedEquipState == "대여"
        ).distinct(models.ManageLog.UsedEquipID).all()
        
        # 겹치는 EquipID 중 ManageLogID가 가장 큰 항목만 유지
        user_rentals = []
        for log in user_current_rentals:
            max_manage_log_id = db.session.query(func.max(models.ManageLog.ManageLogID)).filter(
                models.ManageLog.UserID == current_user_id,
                models.ManageLog.UsedEquipID == log.UsedEquipID,
                models.ManageLog.UsedEquipState == "대여"
            ).scalar()
            
            latest_log = db.session.query(models.ManageLog).filter(
                models.ManageLog.ManageLogID == max_manage_log_id
            ).first()
            
            user_rentals.append({
                "EquipID": latest_log.UsedEquipID,
                # 여기서 필요한 다른 정보들도 추가할 수 있음
            })
        
        # 해당 EquipID들에 대해 다른 사용자가 더 최근에 대여한 기록이 없는지 확인
        final_user_rentals = []
        for rental in user_rentals:
            equip_id = rental["EquipID"]
            other_recent_logs_count = db.session.query(models.ManageLog).filter(
                models.ManageLog.UsedEquipID == equip_id,
                models.ManageLog.UserID != current_user_id,
                models.ManageLog.ManageLogID > max_manage_log_id
            ).count()
            
            if other_recent_logs_count == 0:
                final_user_rentals.append(equip_id)
        
        # 해당 EquipID들에 해당하는 기자재 정보 가져오기
        matched_equipment = db.session.query(models.Equipment).filter(
            or_(*[models.Equipment.EquipID == equip_id for equip_id in final_user_rentals])
        ).all()
        
        return [
            {
                "EquipID": equipment.EquipID,
                "EquipName": equipment.EquipName,
                "EquipInfo": equipment.EquipInfo,
                # 다른 필요한 정보들도 추가 가능
            }
            for equipment in matched_equipment
        ]
