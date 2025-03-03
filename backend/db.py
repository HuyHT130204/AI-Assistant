import sqlite3

conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()

query = "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
cursor.execute(query)
query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
cursor.execute(query)

# query = "INSERT INTO sys_command VALUES (null,'obs', 'C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe')"
# cursor.execute(query)
# conn.commit()

# query = "DELETE FROM web_command WHERE name='facebook'"
# cursor.execute(query)
# conn.commit()

# # testing module
# app_name = "obs"
# cursor.execute('SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
# results = cursor.fetchall()
# print(results[0][0])