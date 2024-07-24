import sqlite3
import Tools.games as games
import Tools.webscrap as webscrap
import Tools.api as api

# Connect to SQLite database
# If the file doesn't exist, it will be created in the current directory.
conn = sqlite3.connect('valplayers.db')

# Create a cursor object
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    kills INTEGER DEFAULT 0,
    deaths INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0
);
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and table created successfully.")

def get_player_kills(player_name):
    conn = sqlite3.connect('valplayers.db')
    cursor = conn.cursor()
    cursor.execute("SELECT kills FROM players WHERE name = ?", (player_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None
    
async def update_player_kills():
    url = await api.get_results_url()
    for match in url:
        if (games.check_if_game_reviewed("https://" + match)):
            print("Game already reviewed")
        else:
            webscrap.parse_and_update_database("https://" + match)
            games.add_game("https://" + match)
            