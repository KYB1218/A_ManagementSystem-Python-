import sqlite3
conn = sqlite3.connect('database.db')
print('create & connect database')

conn.execute(
'''
create table users (ID text, password text, name text, birth int)
'''
)

conn.close()