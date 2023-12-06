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
        "EquipID": fields.String(description="기자재 ID"),
        "EquipState": fields.String(description="기자재 상태"),
        "ID": fields.String(description="사용자 ID"),
        "Name": fields.String(description="사용자 이름"),
        "ManageLogDate": fields.String(description="사용 날짜")
    },
)

parser = ManageLog.parser()  # 헤더를 추가하기 위한 변수
parser.add_argument("Authorization", location="headers")  # 헤더를 입력받기 위해 기대 입력값을 추가

@ManageLog.route("")  # 회원가입의 URL
class ManageLogAdd(Resource):
    @ManageLog.expect(ManageLogField)  # swagger를 통해 데이터베이스를 조작하도록 등록
    def post(self):
        """ManageLog의 정보를 저장하는 API\n
        Id, 비밀번호, 이름, 생년월일을 json의 형태로 전달받아 DB에 저장한다.
        """

        # 데이터 입력값으로부터 가져오기
        ManageLogID = request.json.get("ManageLogID")
        EquipID = request.json.get("EquipID")
        ID = request.json.get("ID")
        Name = request.json.get("Name")
        ManageLogDate = request.json.get("ManageLogDate")

        # user에 맞는 형태로 변환 후 session을 열고 저장
        ManageLog_data = models.ManageLog(ManageLogID=ManageLogID, EquipID=EquipID, ID=ID, Name=Name, ManageLogDate=ManageLogDate)
        db.session.add(ManageLog_data)

        # commit 실행 과정에서 자동으로 rollback이 실행되지 않는 경우가 발생하여 명시적으로 롤백 실행
        try:
            db.session.commit()
            db.session.flush()
        except:
            db.session.rollback()

            return "This ManageLog_data already exist."

        return 0
    
@ManageLog.route("/ManageLogList")
class ManageLogList(Resource):
       @ManageLog.expect(parser)
       def get(self):
        """Equipment 목록을 반환하는 API"""

        manageLog_list = []
        manageLogs = db.session.query(models.ManageLog).all()

        for manageLog in manageLogs:
            manageLog_data = {
                "ManageLogID": manageLog.ManageLogID,
                "EquipID": manageLog.EquipID,
                "ID": manageLog.ID,
                "Name": manageLog.Name,
                "ManageLogDate": manageLog.ManageLogDate
            }
            manageLog_list.append(manageLog_data)

        return manageLog_list