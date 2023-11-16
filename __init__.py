from flask import Flask, render_template, abort, flash, redirect, request, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from . import config

import os
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////workspaces/learning/소개론 코드/db/my_database.db'
# app.config['SECRET_KEY'] = "my_secret"

# if __name__ == "__main__":
#     db.init_app(app)
#     migrate.init_app(app, db)
#     app.run(host = '0.0.0.0', debug=True, port=9999)

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # orm
    db.init_app(app)
    migrate.init_app(app, db)
    from . import models

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/sql_search/<id>')
    def sql_search():
        db_value = db.session.execute("SELECT * from User where id like "+"'%"+id+"%'").fetchall()
        if db_value:
            return render_template('sql_read.html', items = db_value)
        return abort(404, "no database")

    @app.route('/sql_read')
    def sql_read():
        db_value = db.session.query(models.user).all()
        if db_value:
            return render_template('sql_read.html', items = db_value)
        return abort(404, "페이지가 없습니다")

    @app.route('/sql_write', methods = ['GET','POST'])
    def insert_one():
        if request.method == 'POST':
            if not request.form['id'] or not request.form['name'] or not request.form['addr']:
                flash('Fill up the form', 'error')
            else:
                new_data = models.user(int(request.form['id']), request.form['name'], int(request.form['userNFC']))
                db.session.add(new_data)
                db.session.commit()
                flash('DB is saved')
                return redirect(url_for('sql_read'))
        return render_template('sql_write.html')

    return app