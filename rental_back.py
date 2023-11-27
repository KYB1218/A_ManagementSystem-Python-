# 코드
import sqlite3
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from login import app as login_app  # login 모듈에서 Flask 애플리케이션 객체인 app을 가져옴

if not os.path.exists('Equipment.db'):
    conn = sqlite3.connect('Equipment.db')
    print('create & connect database')

    conn.execute(
        '''
        create table Equipment(equipment text PRIMARY KEY, password text, state text, filename text)
        '''
    )
    conn.close()

class Rental:
    @login_app.route('/equipment_form', endpoint='equipment_form')
    def new_user():
        return render_template('equipment.html')

    @login_app.route('/equipment_info', methods=['POST', 'GET'], endpoint='equipment_info')
    def equipment_info():
        con = None

        try:
            if request.method == 'POST':
                equip_name = request.form['equipment_name']
                equip_password = request.form['equip_password']
                state = request.form['state']

                # Get the file from the request
                equip_file = request.files['equipment_file'] 

                if equip_file and equip_file.filename != '':
                    # Securely save the filename
                    filename = secure_filename(equip_file.filename)

                    # Ensure the 'uploads' folder exists
                    if not os.path.exists("uploads"):
                        os.makedirs("uploads")

                    # Save the file to the uploads folder
                    equip_file.save(os.path.join("uploads", filename))

                    # 데이터베이스 연결
                    con = sqlite3.connect("Equipment.db")
                    cur = con.cursor()

                    # 저장된 파일 경로를 데이터베이스에 저장
                    print(equip_name)
                    cur.execute("INSERT INTO Equipment (equipment, password, state, filename) VALUES (?, ?, ?, ?)",
                                (equip_name, equip_password, state, os.path.join("uploads", filename)))

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

        return render_template("result2.html", msg=msg)

    @login_app.route('/equipment_list', endpoint='equipment_list')
    def equipment_list():
        con = sqlite3.connect("Equipment.db")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("select * from Equipment")

        rows = cur.fetchall()
        return render_template("equip_list.html", rows=rows)

    @login_app.route('/search', methods=['GET', 'POST'])
    def search():
        con = sqlite3.connect("Equipment.db")
        con.row_factory = sqlite3.Row

        try:
            if request.method == 'POST':
                search_term = request.form['search_term']

                cur = con.cursor()
                # 검색어를 이용하여 쿼리 실행
                cur.execute("SELECT * FROM Equipment WHERE equipment LIKE ?", ('%' + search_term + '%',))

                rows = cur.fetchall()
                return render_template("equip_list.html", rows=rows)

        except Exception as e:
            print(str(e))
            return "Error: {}".format(str(e))

        finally:
            con.close()

        return render_template("search.html")

if __name__ == '__main__':
    login_app.run(port=80)
