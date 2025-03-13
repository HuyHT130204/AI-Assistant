import csv
import sqlite3

conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()

# Create system command table
query = "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
cursor.execute(query)

# Create web command table
query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
cursor.execute(query)

# Create contacts table if it doesn't exist
query = "CREATE TABLE IF NOT EXISTS contacts(id integer primary key, name VARCHAR(100), Phone VARCHAR(20))"
cursor.execute(query)

# Create facebook contacts table if it doesn't exist
query = """
CREATE TABLE IF NOT EXISTS facebook_contacts(
    id integer primary key, 
    name VARCHAR(100), 
    profile_url VARCHAR(1000),
    last_messaged TIMESTAMP
)
"""
cursor.execute(query)

# Insert Facebook as a web command if it doesn't exist
cursor.execute("SELECT COUNT(*) FROM web_command WHERE name = 'facebook'")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO web_command (name, url) VALUES (?, ?)", 
                  ("facebook", "https://www.facebook.com/"))
    
# Insert Facebook Messenger as a web command if it doesn't exist
cursor.execute("SELECT COUNT(*) FROM web_command WHERE name = 'messenger'")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO web_command (name, url) VALUES (?, ?)", 
                  ("messenger", "https://www.facebook.com/messages/"))

# Commit changes to database
conn.commit()

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

# cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY, name VARCHAR(200), Phone VARCHAR(255), email VARCHAR(255) NULL)''') 

# desired_columns_indices = [0, 20]
 
# with open('contacts.csv', 'r', encoding='utf-8') as csvfile:
#     csvreader = csv.reader(csvfile)
#     for row in csvreader:
#         selected_data = [row[i] for i in desired_columns_indices]
#         cursor.execute(''' INSERT INTO contacts (id, 'name', 'Phone') VALUES (null, ?,? );''', tuple(selected_data))

# conn.commit()
# conn.close()

# print("Data inserted successfully!")

query = "INSERT INTO contacts VALUES (null,'Nhà ❤️', '0377974312', 'null')"
cursor.execute(query)
conn.commit() 

# query = 'HuyThanh'
# query = query.strip().lower()  # Added parentheses to call the method

# cursor.execute("SELECT Phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", 
#                ('%' + query + '%', query + '%'))
# results = cursor.fetchall()
# print(results[0][0])