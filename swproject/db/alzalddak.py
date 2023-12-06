import sqlite3

#만들 데이터베이스 경로 및 이름 지정
database_name = '/workspaces/learning/DB/my_database.db'

#cursor 객체 지정 (이 객체로 실제 db에 내용이 들어가고 지워지고 한다고 함..)
con = sqlite3.connect(database_name)
cursor = con.cursor()

#테이블 생성 (사용자 사용기록 관련 테이블은 추후 추가 예정)
#User 테이블
SQL = "CREATE TABLE IF NOT EXISTS User (UserNFC int primary key not null, UserName text, User_ID int);"
cursor.execute(SQL)
#Equipment 테이블 (NFC 스티커가 붙어있는 물건)
SQL = "CREATE TABLE IF NOT EXISTS Equipment (ProductNFC int primary key not null, PName text, State text);"
cursor.execute(SQL)

#Insert
def insert_User(userNFC, userName, userID):
    con = sqlite3.connect(database_name)
    cursor = con.cursor()

    SQL = "INSERT INTO User VALUES(?,?,?);"
    cursor.execute(SQL, (userNFC, userName, userID))

    con.commit()
    con.close()

def insert_Equipment(productNFC, pName, state):
    con = sqlite3.connect(database_name)
    cursor = con.cursor()

    SQL = "INSERT INTO Equipment VALUES(?,?,?);"
    cursor.execute(SQL, (productNFC, pName, state))

    con.commit()
    con.close()

#Search    
def search_User():
    con = sqlite3.connect(database_name)
    cursor = con.cursor()

    SQL = "SELECT * FROM User;"
    cursor.execute(SQL)

    print(cursor.fetchall())

def search_Equipment():
    con = sqlite3.connect(database_name)
    cursor = con.cursor()

    SQL = "SELECT * FROM Equipment;"
    cursor.execute(SQL)

    print(cursor.fetchall()) 

#Delete
def delete_User(userID):
    con = sqlite3.connect(database_name)
    cursor = con.cursor()

    SQL = "DELETE FROM User WHERE userID = ?;"
    cursor.execute(SQL, (userID, ))

    con.commit()
    con.close()

def delete_Equipment(productNFC):
    con = sqlite3.connect(database_name)
    cursor = con.cursor()

    SQL = "DELETE FROM Equipment WHERE productNFC = ?;"
    cursor.execute(SQL, (productNFC, ))

    con.commit()
    con.close()

insert_User(123456, '안현진', 2021011333)
insert_User(456789, '구아영', 2021011301)
search_User()

insert_Equipment(987654,'춘식이 인형','대여 불가능')
insert_Equipment(654321, '현대제어공학 5판','대여 가능')
search_Equipment()

con.close()