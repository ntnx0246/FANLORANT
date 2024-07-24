import requests
import sqlite3
from bs4 import BeautifulSoup

def create_database_connection():
    """ Establishes a connection to the SQLite database. """
    conn = sqlite3.connect('valplayers.db')
    return conn

def close_database_connection(conn):
    """ Closes the connection to the database. """
    conn.close()

def fetch_page_content(url):
    """ Fetches and returns the HTML content of a given URL. """
    response = requests.get(url)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    return response.text

def parse_and_update_database(url):
    """ Parses HTML content to find player data and updates the database accordingly. """
    conn = create_database_connection()
    cursor = conn.cursor()
    html_content = fetch_page_content(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    stats_game = soup.find('div', {'class': 'vm-stats-game mod-active', 'data-game-id': 'all'})

    if stats_game:
        players = stats_game.find_all('tr')
        for player in players:
            name_tag = player.find('td', class_='mod-player')
            kills_tag = player.find('td', class_='mod-vlr-kills')

            if name_tag and kills_tag:
                name = ' '.join(name_tag.text.strip().split()).split()[0]  # First word, assuming it's the player name
                kills = ' '.join(kills_tag.text.strip().split()).split()[0]  # Top kill count
                add_or_update_player_kills(name, int(kills), cursor)
        print("Database updated successfully.")
    else:
        print("Stats section not found on the page.")
    conn.commit()
    close_database_connection(conn)

def add_or_update_player_kills(name, new_kills, cursor):
    """ Adds or updates a player's kill count in the database. """
    cursor.execute('SELECT kills FROM players WHERE name = ?', (name,))
    result = cursor.fetchone()
    if result:
        # Player exists, update their kills
        current_kills = result[0]
        total_kills = current_kills + new_kills
        cursor.execute('UPDATE players SET kills = ? WHERE name = ?', (total_kills, name))
    else:
        # Player does not exist, insert new record
        cursor.execute('INSERT INTO players (name, kills) VALUES (?, ?)', (name, new_kills))

# Example usage
if __name__ == "__main__":
    url = "https://www.example.com/path_to_page_with_player_stats"
    parse_and_update_database(url)
