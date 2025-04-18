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

# Create learned_commands table if it doesn't exist
query = """
CREATE TABLE IF NOT EXISTS learned_commands(
    id INTEGER PRIMARY KEY,
    command_type VARCHAR(50),
    pattern VARCHAR(200),
    platform VARCHAR(100),
    url_template VARCHAR(500),
    count INTEGER DEFAULT 1,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
cursor.execute(query)

# Create settings table if it doesn't exist
query = """
CREATE TABLE IF NOT EXISTS settings(
    id INTEGER PRIMARY KEY,
    category VARCHAR(50),
    key VARCHAR(100),
    value TEXT,
    modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

# Insert default learned commands if they don't exist
default_commands = [
    # Search commands
    ("search", "search (.*) on google", "google", "https://www.google.com/search?q={query}"),
    ("search", "search (.*) on youtube", "youtube", "https://www.youtube.com/results?search_query={query}"),
    ("search", "search (.*) on instagram", "instagram", "https://www.instagram.com/explore/tags/{query}/"),
    ("search", "search (.*) on twitter", "twitter", "https://twitter.com/search?q={query}"),
    ("search", "search (.*) on tiktok", "tiktok", "https://www.tiktok.com/search?q={query}"),
    
    # Play commands
    ("play", "play (.*) on spotify", "spotify", "https://open.spotify.com/search/{query}"),
    ("play", "play (.*) on youtube", "youtube", "https://www.youtube.com/results?search_query={query}"),
    ("play", "play (.*) on zing mp3", "zing mp3", "https://zingmp3.vn/tim-kiem/bai-hat?q={query}"),
    ("play", "play (.*) on nhaccuatui", "nhaccuatui", "https://www.nhaccuatui.com/tim-kiem?q={query}"),
]

for command_type, pattern, platform, url_template in default_commands:
    cursor.execute(
        "SELECT COUNT(*) FROM learned_commands WHERE command_type = ? AND platform = ?",
        (command_type, platform)
    )
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO learned_commands (command_type, pattern, platform, url_template) VALUES (?, ?, ?, ?)",
            (command_type, pattern, platform, url_template)
        )

# Commit changes to database
conn.commit()

# Use this block only when you want to add a new contact
# query = "INSERT INTO contacts VALUES (null,'Nhà ❤️', '0377974312', 'null')"
# cursor.execute(query)
# conn.commit()