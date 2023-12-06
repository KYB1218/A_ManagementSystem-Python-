import ssl

from flask import Flask
from flask_restx import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import config

# api 함수 호출
from .apidir.UserApi import User
from .apidir.EquipmentApi import Equipment
from .apidir.DeleteLogApi import DeleteLog
from .apidir.ManageLogApi import ManageLog

from flask_migrate import Migrate

app = Flask(__name__)

CORS(app, resources={r"*": {"origins": "*"}})  # 외부 접속을 허용하는 함수

api = Api(
    app,
    title="DB Server Api",
    description="데이터베이스와 통신하기 위한 서버입니다.\n \
                 User, Equipment, ManageLog, DeleteLog Table이 존재합니다.\n \
                 로그인 이후에는 기능을 사용하기 위해 jwt 토큰을 헤더를 통해 전송해야합니다.",
)

# auth
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
app.config["PROPAGATE_EXCEPTIONS"] = True
jwt = JWTManager(app)

# orm
db = SQLAlchemy()

# 데이터베이스 초기화
app.config.from_object(config)
db.init_app(app)

import models

migrate = Migrate(app, db)

# api 등록
api.add_namespace(User, "/User")
api.add_namespace(Equipment, "/Equipment")
api.add_namespace(DeleteLog, "/DeleteLog")
api.add_namespace(ManageLog, "/ManageLog")

# flask 서버 시작
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)