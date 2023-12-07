import datetime

from flask import request
from flask_restx import Resource, Api, Namespace, fields
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import bcrypt  # 로그인 비밀번호 암호화를 위한 라이브러리
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

import models

db = models.db  # app.py에서 sqlalchemy 호출시 순환 호출 오류 발생하여 각 api마다 호출

DeleteLog = Namespace("DeleteLog", description="DeleteLog DB(삭제 기록을 저장하는 DB)와 통신하는 Api")

# swagger 문서화를 위한 모델 정의
DeleteLogField = DeleteLog.model(
    "DeleteLog",
    {
        "DeleteLogID": fields.String(description="DeleteLog ID"),
        "DeletedEquipID": fields.String(description="기자재 ID"),
        "DeletedEquipName": fields.String(description="기자재 이름"),
        "DeletedEquipInfo": fields.String(description="기자재 상세 정보"),
        "DeletedEquipState": fields.String(description="기자재 상태"),
        "DeleterID": fields.String(description="사용자 ID"),
        "DeleterName": fields.String(description="사용자 이름"),
        "DeletedDate": fields.String(description="삭제 날짜")
    },
)

parser = DeleteLog.parser()  # 헤더를 추가하기 위한 변수
parser.add_argument("Authorization", location="headers")  # 헤더를 입력받기 위해 기대 입력값을 추가

#기자재 목록    
@DeleteLog.route("")
class DeleteLogList(Resource):
       @jwt_required()
       @DeleteLog.expect(parser)
       def get(self):
        """DeleteLog 목록을 반환하는 API"""

        deletelog_list = []
        deletelogs = db.session.query(models.DeleteLog).all()

        for deletelog in deletelogs:
            deletelog_data = {
                "DeleteLogID": deletelog.DeleteLogID,
                "DeletedEquipID": deletelog.DeletedEquipID,
                "DeletedEquipName": deletelog.DeletedEquipName,
                "DeletedEquipInfo": deletelog.DeletedEquipInfo,
                "DeletedEquipState": deletelog.DeletedEquipState,
                "DeleterID": deletelog.DeleterID,
                "DeleterName": deletelog.DeleterName,
                "DeletedDate": deletelog.DeletedDate
            }
            deletelog_list.append(deletelog_data)

        return deletelog_list
       
@DeleteLog.route("/Restore/<DID>")
class RestoreEquip(Resource):
    @jwt_required()
    @DeleteLog.expect(parser)
    def put(self, DID):
        """DeleteLog에 있는 정보를 복원하여 Equipment 테이블에 추가하는 API\n
        DeleteLog의 ID를 입력받아 해당 ID의 정보를 검색하고 Equipment 테이블에 추가한다.\n
        jwt 인증의 경우 헤더에 Authorization: Bearer jwt를 입력하여야 한다."""

        delete_log = models.DeleteLog.query.filter_by(DeleteLogID=DID).first()

        if delete_log:
            equipment_data = {
                "EquipID": delete_log.DeletedEquipID,
                "EquipName": delete_log.DeletedEquipName,
                "EquipInfo": delete_log.DeletedEquipInfo,
                "EquipState": delete_log.DeletedEquipState
            }

            equipment = models.Equipment(**equipment_data)
            db.session.add(equipment)
            db.session.commit() 

            db.session.delete(delete_log)
            db.session.commit()

            return f"Deleted Equipment {delete_log.DeletedEquipID} restored successfully."
        else:
            return f"DeleteLog {DID} not found."