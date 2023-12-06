import datetime

from flask import request
from flask_restx import Resource, Api, Namespace, fields
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import bcrypt  # 로그인 비밀번호 암호화를 위한 라이브러리
from flask_jwt_extended import jwt_required, create_access_token

import models

db = SQLAlchemy() # app.py에서 sqlalchemy 호출시 순환 호출 오류 발생하여 각 api마다 호출

User = Namespace("User", description="User DB(User의 정보를 저장하는 DB)와 통신하는 Api")

# swagger 문서화를 위한 모델 정의
UserField = User.model(
    "User",
    {
        "ID": fields.String(description="사용자 ID"),
        "PassWd": fields.String(description="비밀번호"),
        "Name": fields.String(description="사용자 이름"),
    },
)

parser = User.parser()  # 헤더를 추가하기 위한 변수
parser.add_argument("Authorization", location="headers")  # 헤더를 입력받기 위해 기대 입력값을 추가


@User.route("",methods=['GET', 'POST'])  # 회원가입의 URL
class UserAdd(Resource):
    @User.expect(UserField)  # swagger를 통해 데이터베이스를 조작하도록 등록
    def post(self):
        """User의 정보를 저장하는 API\n
        Id, 비밀번호, 이름, 생년월일을 json의 형태로 전달받아 DB에 저장한다.
        """
       
        # 데이터 입력값으로부터 가져오기
        ID = request.json.get("ID")
        PassWd = bcrypt.hashpw(
            request.json.get("PassWd").encode("utf-8"), bcrypt.gensalt()
        )
        Name = request.json.get("Name")

        # user에 맞는 형태로 변환 후 session을 열고 저장
        User_data = models.User(ID=ID, PassWd=PassWd, Name=Name)
        db.session.add(User_data)

        # commit 실행 과정에서 자동으로 rollback이 실행되지 않는 경우가 발생하여 명시적으로 롤백 실행
        try:
            db.session.commit()
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            print(str(e.args))
            return str(e.args)

        return 0

@User.route("/<UID>")
class UserEdit(Resource):
    @jwt_required()  # jwt 검증
    @User.expect(parser)  # 입력값 추가
    def get(self, UID):
        """User의 정보를 가져오는 API\n
        ID를 입력받아 해당 ID와 동일한 User의 성별, 직업, 나이를 반환한다.\
        jwt 인증의 경우 헤더에 Authorization: Bearer jwt를 입력하여야 한다.
        """

        data = db.session.query(models.User).filter(models.User.ID.like(UID)).first()

        # 존재하지 않는 사용자의 정보를 요청한 경우
        try:
            return {"ID": data.ID, "Name": data.Name, "PassWd": data.PassWd}
        except AttributeError:
            return "This User doesn't exist"

    @User.expect(UserField)
    def post(self, UID):
        """User 로그인 API\n
        로그인 정보를 받아 옳을 경우 jwt 문자열, 아닐경우 1을 반환한다.
        id가 존재하지 않는 경우는 2를 반환한다.
        PassWd만 Json의 형태로 전송하면 된다.
        """

        ID = UID

        data = db.session.query(models.User).filter(models.User.ID.like(ID)).first()
        try:
            PW = bcrypt.checkpw(
                request.json.get("PassWd").encode("utf-8"), data.PassWd
            )  # 비밀번호 검증. 만약 id가 존재하지 않으면 attributeError가 발생한다.
        except AttributeError:
            return 2

        if PW == True:
            access_token = create_access_token(identity=UID)  # jwt 암호화 및 전송
            return access_token
        else:
            return 1