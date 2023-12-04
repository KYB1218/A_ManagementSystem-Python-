import sqlite3
from flask import Flask, render_template, request
import os
from rental_back import login_app as rental_app


if not os.path.exists('UserLog.db'):
    conn = sqlite3.connect('UserLog.db')
    print('create & connect database')

    conn.execute(
        '''
        create table Equipment(user_name text PRIMARY KEY, day text, now_state text)
        '''
    )
    conn.close()
    
@rental_app.route("/rental")
def rental():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the rows from the Equipment table
    cursor.execute("SELECT * FROM Equipment")
    rows = cursor.fetchall()

    # Render the template with the rows
    return render_template("nypage.html", rows=rows)

@rental_app.route("/update_state/<equipment_name>")
def update_state(equipment_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Update the state to '대여중' for the specified equipment_name
    cursor.execute("UPDATE Equipment SET state='대여중' WHERE equipment=?", (equipment,))

    conn.commit()
    conn.close()

    # Redirect back to the rental page after updating the state
    return redirect("/rental")


@login_app.route('/equipment_list', endpoint='equipment_list')
    def equipment_list():
        con = sqlite3.connect("Equipment.db")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("select * from Equipment")

        rows = cur.fetchall()
        return render_template("equip_list.html", rows=rows)
    
    if not os.path.exists('EquipmentLog.db'):
        conn = sqlite3.connect('EquipmentLog.db')
    print('create & connect database')

    conn.execute(
        '''
        create table Equipment(equipment_name text PRIMARY KEY, day text, now_state text)
        '''
    )
    conn.close()
    

    @login_app.route('/delate', methods=['GET', 'POST'])
    def search():
        con = sqlite3.connect("Equipment.db")
        con.row_factory = sqlite3.Row

        try:
            if request.method == 'POST':
                search_term = request.form['search_term']

                cur = con.cursor()
                # 검색어를 이용하여 쿼리 실행
                cur.execute("Delect * FROM Equipment WHERE equipment LIKE ?", ('%' + search_term + '%',))
                
                con = sqlite3.connect("EquipmentLog.db")
                cur = con.cursor()

                # 저장된 파일 경로를 데이터베이스에 저장
                cur.execute("INSERT INTO User(ID, day, now_state) VALUES (?, ?, ?)",
                            (equip_id, day, now_state))

                con.commit()  # 변경사항 저장

                rows = cur.fetchall()
                return render_template("equip_list.html", rows=rows)

        except Exception as e:
            print(str(e))
            return "Error: {}".format(str(e))

        finally:
            con.close()

        return render_template("search.html")
if __name__ == '__main__':
    rental_app.run(port=80)
