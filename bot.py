import discord
from discord import app_commands
import asyncio
from dotenv import load_dotenv
import os
import Tools.database as database
import Tools.api as api
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

@tree.command(name="news", description="Get news about Val stuff idk")
async def fetch_news(interaction: discord.Interaction, number_of_articles: app_commands.Range[int, 1, 10] = 3):    
    await interaction.response.defer()
    await api.send_news_embed(interaction, number_of_articles)  

@tree.command(name="upcoming_matches", description="Get info abt upcoming matches likely won't work :D")
async def fetch_matches(interaction: discord.Interaction, number_of_games: app_commands.Range[int, 1, 10] = 3):    
    await interaction.response.defer()
    await api.send_upcoming_games_embed(interaction, number_of_games)

@tree.command(name="player_info", description="Get info abt a specific player")
async def fetch_info(interaction: discord.Interaction, player_name: str = "TenZ", region: str = "na"):    
    await interaction.response.defer()
    await api.send_player_embed(interaction, player_name, region) 

@tree.command(name="update_database", description="Update the database with the latest player kills")
async def update_database(interaction: discord.Interaction):    
    await interaction.response.defer(ephemeral=True)  # Defer the response
    try:
        await database.update_player_kills()
        await interaction.followup.send("Database updated successfully.")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")

@tree.command(name="get_kills", description="Get the kill count of a specific player")
async def get_kills(interaction: discord.Interaction, player_name: str):
    kills = database.get_player_kills(player_name)
    if kills is not None:
        await interaction.response.send_message(f"{player_name} has {kills} kills.")
    else:
        await interaction.response.send_message("Player not found in the database.")

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event 
async def on_message(message):
    if message.author == client.user:
        return

async def setup():
    # Sync to a specific guild
    print("Syncing commands...")
    commands = await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Commands synced: {commands}")
    await tree.sync()

def schedule_update():
    while True:
        schedule.run_pending()
        time.sleep(1)

def update_database():
    try:
        database.update_player_kills()
        print("Database updated successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Schedule the update to run every hour
schedule.every().hour.do(update_database)
thread = Thread(target=schedule_update)
thread.start()

client.setup_hook = setup

client.run(BOT_TOKEN)