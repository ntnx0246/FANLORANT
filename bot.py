import discord
from discord import app_commands
import asyncio
from dotenv import load_dotenv
import os
import Tools.database as database
import Tools.games as games
import Tools.api as api
import Tools.webscrap as webscrap
import schedule
import time
from threading import Thread

# Load environment variables
load_dotenv('token.env')

# Retrieve the bot token and guild ID from the environment
BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))
channel_id = os.getenv('CHANNEL_ID')

# Set up intents for the bot
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

# Initialize the command tree for the client
tree = app_commands.CommandTree(client)

@tree.command(name="news", description="Get recent news articles about Valorant")
async def fetch_news(interaction: discord.Interaction, number_of_articles: app_commands.Range[int, 1, 10] = 3):    
    await interaction.response.defer()
    await api.send_news_embed(interaction, number_of_articles)

@tree.command(name="upcoming_matches", description="Get info about upcoming matches")
async def fetch_matches(interaction: discord.Interaction, number_of_games: app_commands.Range[int, 1, 10] = 3):    
    await interaction.response.defer()
    await api.send_upcoming_games_embed(interaction, number_of_games)

@tree.command(name="update_database", description="Update the database with the latest player kills")
async def update_database_command(interaction: discord.Interaction):    
    await interaction.response.defer(ephemeral=True)  # Defer the response
    try:
        await database.update_player_kills()
        await interaction.followup.send("Database updated successfully.")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")

@tree.command(name="get_kda", description="Get the kda of a specific player")
async def get_kda(interaction: discord.Interaction, player_name: str):
    kills = database.get_player_kills(player_name)
    deaths = database.get_player_deaths(player_name)
    assists = database.get_player_assists(player_name)
    if kills is not None:
        await interaction.response.send_message(f"{player_name} has {kills} kills, {deaths} deaths, and {assists} assists.")
    else:
        await interaction.response.send_message("Player not found in the database.")

@tree.command(name="get_points", description="Get the points of a specific player")
async def get_points(interaction: discord.Interaction, player_name: str):
    points = database.get_player_points(player_name)
    if points is not None:
        await interaction.response.send_message(f"{player_name} has {points} points.")
    else:
        await interaction.response.send_message("Player not found in the database.")

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event 
async def on_message(message):
    if message.author == client.user:
        return

def schedule_update():
    while True:
        schedule.run_pending()
        time.sleep(1)

async def setup():
    # Sync to a specific guild
    print("Syncing commands...")
    commands = await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Commands synced: {commands}")

# Schedule the update to run every hour
schedule.every().hour.do(lambda: asyncio.run_coroutine_threadsafe(update_database_command(None), client.loop))
thread = Thread(target=schedule_update)
thread.start()

client.setup_hook = setup

client.run(BOT_TOKEN)
