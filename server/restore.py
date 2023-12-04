import sqlite3
from datetime import datetime
from flask import Flask, render_template, abort, flash, redirect, request, url_for, render_template
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
migrate = Migrate()

if not os.path.exists('EquipmentLog.db'):
    conn = sqlite3.connect('EquipmentLog.db')
    print('create & connect database')

    conn.execute(
    '''
    create table users (Equipment text PRIMARY KEY, RentalTime text, RenterUser text)
    '''
    )
    conn.close()