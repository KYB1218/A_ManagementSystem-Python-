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

            msg = "Success"

        except Exception as e:
            print(str(e))
            if con:
                con.rollback()
            msg = "Error: {}".format(str(e))

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
        
    @app.route('/sql_read/<int:myid>')
    def sql_read(myid):
        con=sqlite3.connect("User.db")
        con.row_factory=sql.Row
            
        cur=con.cursor()
        cur.execute("select * from users id=?", myid)
            
        rows = cur.fetchall()
        if True:
            return render_template("list.html", rows=rows)
        else:
            return abort(404, "no database")
        
    
    if __name__ == '__main__':
        app.run(port=80)   

