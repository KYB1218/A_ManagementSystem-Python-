import sqlite3
from datetime import datetime
from flask import Flask, render_template, abort, flash, redirect, request, url_for, render_template
#from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
#migrate = Migrate()

if not os.path.exists('User.db'):
    conn = sqlite3.connect('User.db')
    print('create & connect database')

    conn.execute(
    '''
    create table User(ID text PRIMARY KEY, password text, birth text, name text)
    '''
    )
    conn.close()

class Login(object): 
    @app.route('/')
    def home():
            return render_template('index.html')


    @app.route('/user_form')
    def new_user():
        return render_template('user.html')

    @app.route('/user_info', methods=['POST', 'GET'])
    def user_info():
        con = None

        try:
            if request.method == 'POST':
                user_id = request.form['user_id']
                user_password = request.form['user_password']
                birth = request.form['birth']
                name = request.form['name']

                con = sqlite3.connect("User.db")
                cur = con.cursor()

                # 저장된 파일 경로를 데이터베이스에 저장
                cur.execute("INSERT INTO User(ID, password, birth, name) VALUES (?, ?, ?,?)",
                            (user_id, user_password, birth, name))

                con.commit()  # 변경사항 저장

            msg = "회원가입이 완료되었습니다"

        except Exception as e:
            print(str(e))
            if con:
                con.rollback()
            msg = "정보를 다시 입력해주세요 {}".format(str(e))

        finally:
            if con:
                con.close()

        return render_template("result1.html", msg=msg)


    @app.route('/user_list')
    def list():
        try:
            con = sqlite3.connect("User.db")
            con.row_factory = sqlite3.Row

            cur = con.cursor()
            cur.execute("select * from User")

            rows = cur.fetchall()
            return render_template("user_list.html", rows=rows)
        
        except Exception as e:
            print("Error: {}".format(str(e)))
            return "Internal Server Error"  

        finally:
            if con:
                con.close()
        
    @app.route('/login', methods=['GET', 'POST'])
    def log_in():
        con = sqlite3.connect("User.db")
        con.row_factory = sqlite3.Row

        try:
            if request.method == 'POST':
                my_id = request.form['my_id']
                my_password = request.form['my_password']

                cur = con.cursor()
                # 검색어를 이용하여 쿼리 실행
                cur.execute("SELECT * FROM User WHERE ID LIKE ?", ('%' + my_id + '%',))

                rows1 = cur.fetchall()
                my_password = request.form['my_password']
                cur = con.cursor()
                # 검색어를 이용하여 쿼리 실행
                cur.execute("SELECT * FROM User WHERE password LIKE ?", ('%' + my_password + '%',))

                rows2 = cur.fetchall()
                return redirect(url_for('mypage', my_id=my_id))


        except Exception as e:
            print(str(e))
            return "Error: {}".format(str(e))

        finally:
            con.close()

        return render_template("login.html")
        
    @app.route('/sql_read/<my_id>', methods=['GET', 'POST'])
    def mypage(my_id):
        con = sqlite3.connect("User.db")
        con.row_factory = sqlite3.Row

        try:
            cur = con.cursor()
            # 검색어를 이용하여 쿼리 실행
            cur.execute("SELECT * FROM User WHERE ID LIKE ?", ('%' + my_id + '%',))
            rows1 = cur.fetchall()
            
            # 이 부분에서 my_password 변수를 다시 정의하지 않도록 수정
            cur.execute("SELECT * FROM User WHERE password LIKE ?", ('%' + my_id + '%',))
            rows2 = cur.fetchall()

            if not rows1 or not rows2:
                # 검색 결과가 없는 경우 처리
                return render_template("no_results.html")
            
            return render_template("mypage.html", rows1=rows1, rows2=rows2)

        except Exception as e:
            print(str(e))
            return "Error: {}".format(str(e))

        finally:
            

            rows = cur.fetchall()
            return render_template("equip_list.html")

    
    if __name__ == '__main__':
        app.run(port=80)  
