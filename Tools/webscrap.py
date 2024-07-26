import requests
import sqlite3
from bs4 import BeautifulSoup

def create_database_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect('valplayers.db')
    return conn

def close_database_connection(conn):
    """Closes the connection to the database."""
    conn.close()

def fetch_page_content(url):
    """Fetches and returns the HTML content of a given URL."""
    response = requests.get(url)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    return response.text

def extract_first_number(text):
    """Extracts the first valid integer from the given text."""
    for part in text.split():
        try:
            return int(part)
        except ValueError:
            continue
    return 0

def extract_player_name(full_name):
    """Extracts the player name from the full name, assuming the player name is the first part."""
    return full_name.split()[0]  # Take the first part of the name

def ensure_points_column():
    """Ensures that the points column exists in the players table."""
    conn = create_database_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE players ADD COLUMN points REAL DEFAULT 0')
    except sqlite3.OperationalError:
        # Ignore the error if the column already exists
        pass
    conn.commit()
    close_database_connection(conn)

def parse_and_update_database(url):
    """Parses HTML content to find player data and updates the database accordingly."""
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
            deaths_tag = player.find('td', class_='mod-vlr-deaths')
            assists_tag = player.find('td', class_='mod-vlr-assists')

            if name_tag and kills_tag and deaths_tag and assists_tag:
                full_name = ' '.join(name_tag.text.strip().split())
                player_name = extract_player_name(full_name)
                kills = extract_first_number(kills_tag.text.strip())
                deaths = extract_first_number(deaths_tag.text.strip())
                assists = extract_first_number(assists_tag.text.strip())

                add_or_update_player_stats(player_name, kills, deaths, assists, cursor)
        print("Database updated successfully.")
    else:
        print("Stats section not found on the page.")
    
    conn.commit()
    close_database_connection(conn)

def add_or_update_player_stats(name, kills, deaths, assists, cursor):
    """Adds or updates a player's stats and points in the database."""
    cursor.execute('SELECT kills, deaths, assists, points FROM players WHERE name = ?', (name,))
    result = cursor.fetchone()
    points = kills * 1 + deaths * -0.5 + assists * 0.25  # Calculate points based on the criteria
    
    if result:
        current_kills, current_deaths, current_assists, current_points = result
        total_kills = current_kills + kills
        total_deaths = current_deaths + deaths
        total_assists = current_assists + assists
        total_points = current_points + points  # Add the new points to the existing points
        cursor.execute('UPDATE players SET kills = ?, deaths = ?, assists = ?, points = ? WHERE name = ?',
                       (total_kills, total_deaths, total_assists, total_points, name))
    else:
        cursor.execute('INSERT INTO players (name, kills, deaths, assists, points) VALUES (?, ?, ?, ?, ?)',
                       (name, kills, deaths, assists, points))

def remove_all_players():
    """Removes all players from the database."""
    conn = create_database_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM players')
    conn.commit()
    close_database_connection(conn)

# Ensure the points column exists
ensure_points_column()

# Example usage
if __name__ == "__main__":
    url = "https://www.vlr.gg/360911/justus-vs-zol-esports-challengers-league-2024-philippines-split-2-lr1"
    parse_and_update_database(url)
