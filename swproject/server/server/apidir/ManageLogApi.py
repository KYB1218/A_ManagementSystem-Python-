import datetime

from flask import request
from flask_restx import Resource, Api, Namespace, fields
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import bcrypt  # 로그인 비밀번호 암호화를 위한 라이브러리
from flask_jwt_extended import jwt_required, create_access_token

import models

db = SQLAlchemy()  # app.py에서 sqlalchemy 호출시 순환 호출 오류 발생하여 각 api마다 호출

ManageLog = Namespace("ManageLog", description="ManageLog DB(ManageLog의 정보를 저장하는 DB)와 통신하는 Api")

# swagger 문서화를 위한 모델 정의
ManageLogField = ManageLog.model(
    "ManageLog",
    {
        "ManageLogID": fields.String(description="ManageLog ID"),
        "UsedEquipID": fields.String(description="기자재 ID"),
        "UsedEquipState": fields.String(description="기자재 상태"),
        "UserID": fields.String(description="사용자 ID"),
        "UserName": fields.String(description="사용자 이름"),
        "ManageLogDate": fields.String(description="사용 날짜")
    },
)

parser = ManageLog.parser()  # 헤더를 추가하기 위한 변수
parser.add_argument("Authorization", location="headers")  # 헤더를 입력받기 위해 기대 입력값을 추가
    
@ManageLog.route("")
class ManageLogList(Resource):
       @ManageLog.expect(parser)
       def get(self):
        """ManageLog 목록을 반환하는 API"""

        manageLog_list = []
        manageLogs = db.session.query(models.ManageLog).all()

        for manageLog in manageLogs:
            manageLog_data = {
                "ManageLogID": manageLog.ManageLogID,
                "UsedEquipID": manageLog.UsedEquipID,
                "UsedEquipState": manageLog.UsedEquipState,
                "UserID": manageLog.UserID,
                "UserName": manageLog.UserName,
                "ManageLogDate": manageLog.ManageLogDate
            }
            manageLog_list.append(manageLog_data)

        return manageLog_list