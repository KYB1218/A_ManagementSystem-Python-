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
        "EquipID": fields.String(description="기자재 ID"),
        "EquipName": fields.String(description="기자재 이름"),
        "EquipInfo": fields.String(description="기자재 상세 정보"),
        "EquipState": fields.Boolean(description="기자재 상태"),
        "ID": fields.String(description="사용자 ID"),
        "Name": fields.String(description="사용자 이름"),
        "DeletedDate": fields.String(description="삭제 날짜")
    },
)

parser = DeleteLog.parser()  # 헤더를 추가하기 위한 변수
parser.add_argument("Authorization", location="headers")  # 헤더를 입력받기 위해 기대 입력값을 추가

@DeleteLog.route("")  # DeleteLog 추가
class DeleteAdd(Resource):
    @DeleteLog.expect(DeleteLogField)  # swagger를 통해 데이터베이스를 조작하도록 등록
    def post(self):
        """삭제 기록 정보를 저장하는 API\n
        기자재의 Id, 이름, 상세정보, 상태와 사용자의 ID, 이름, 그리고 삭제 날짜와 Log ID를 json의 형태로 전달받아 DB에 저장한다.
        """

        # 데이터 입력값으로부터 가져오기
        DeleteLogID = request.json.get("DeleteLogID")
        EquipID = request.json.get("EquipID")
        EquipName = request.json.get("EquipName")
        EquipInfo = request.json.get("EquipInfo")
        EquipState = request.json.get("EquipState")
        ID = request.json.get("ID")
        Name = request.json.get("Name")
        DeletedDate = request.json.get("DeletedDate")

        # DeleteLog에 맞는 형태로 변환 후 session을 열고 저장
        DeleteLog_data = models.User(DeletedLogID=DeleteLogID, EquipID=EquipID, EquipName=EquipName,
                                     EuipInfo=EquipInfo, EquipState=EquipState, ID=ID, Name=Name, DeletedDate=DeletedDate)
        db.session.add(DeleteLog_data)

        # commit 실행 과정에서 자동으로 rollback이 실행되지 않는 경우가 발생하여 명시적으로 롤백 실행
        try:
            db.session.commit()
            db.session.flush()
        except:
            db.session.rollback()

            return "This log already exist."

        return 0


#기자재 목록    
@DeleteLog.route("/DeleteLogList")
class DeleteLogList(Resource):
       @DeleteLog.expect(parser)
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