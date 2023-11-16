import os

BASE_DIR = os.path.dirname(__file__)
# basdir 경로안에 DB파일 만들기
dbfile = os.path.join(BASE_DIR, 'db.sqlite')
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'NFC.db'))
# 비지니스 로직이 끝날때 Commit 실행(DB반영)
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = False