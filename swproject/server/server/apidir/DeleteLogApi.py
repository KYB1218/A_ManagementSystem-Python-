import datetime

from flask import request
from flask_restx import Resource, Api, Namespace, fields
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import bcrypt  # 로그인 비밀번호 암호화를 위한 라이브러리
from flask_jwt_extended import jwt_required, create_access_token

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
       @DeleteLog.expect(parser)
       def get(self):
        """DeleteLog 목록을 반환하는 API"""

        deleteLog_list = []
        deleteLogs = db.session.query(models.DeleteLog).all()

        for deleteLog in deleteLogs:
            deleteLog_data = {
                "DeleteLogID": deleteLog.DeleteLogID,
                "DeletedEquipID": deleteLog.DeletedEquipID,
                "DeletedEquipName": deleteLog.DeletedEquipName,
                "DeletedEquipInfo": deleteLog.DeletedEquipInfo,
                "DeletedEquipState": deleteLog.DeletedEquipState,
                "DeleterID": deleteLog.DeleterID,
                "DeleterName": deleteLog.DeleterName,
                "DeletedDate": deleteLog.DeletedDate
            }
            deleteLog_list.append(deleteLog_data)

        return deleteLog_list
       
       