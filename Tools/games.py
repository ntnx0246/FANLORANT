import sqlite3

def create_database():
    # Connect to the SQLite database (it will be created if it does not exist)
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()

    # Create the table if it does not exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviewed_games (
        url TEXT PRIMARY KEY
    );
    ''')
    conn.commit()
    conn.close()

def add_game(url):
    """ Add a new game URL to the database if it doesn't already exist. """
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()

    # Check if the URL already exists
    cursor.execute("SELECT url FROM reviewed_games WHERE url = ?", (url,))
    if cursor.fetchone() is None:
        # Insert the new URL if it does not exist
        cursor.execute("INSERT INTO reviewed_games (url) VALUES (?)", (url,))
        conn.commit()
        print(f"URL added: {url}")
    else:
        print("URL already exists in the database.")
    
    conn.close()

def check_if_game_reviewed(url):
    """ Check if a game has already been reviewed by searching for its URL. """
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM reviewed_games WHERE url = ?", (url,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

# Example usage
# if __name__ == "__main__":
#     create_database()
#     add_game("https://example.com/game/123")
#     if check_if_game_reviewed("https://example.com/game/123"):
#         print("This game has been reviewed.")
#     else:
#         print("This game has not been reviewed.")
