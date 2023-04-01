import discord
import prettytable

from service.match_watcher import MatchWatcher
from service.faceit_data_api import FaceitData
from pprint import pprint

DISCORD_BOT_TOKEN=""
FACEIT_API_KEY=""
# DISCORD_BOT_TOKEN=os.getenv("DISCORD_BOT_TOKEN")
BOT_CHANNEL_NAME="bot-test"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
faceit_data = FaceitData(FACEIT_API_KEY)
hub_id = "e5c0f56b-8bd4-4ad1-a9fe-524e88b2477f"
player_elos = {}

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    channels = list(client.get_all_channels())
    bot_channel = [channel for channel in channels if channel.name == BOT_CHANNEL_NAME][0]
    match_watcher = MatchWatcher(bot_channel, hub_id, faceit_data, player_elos)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content == '/leaderboard':
        ranking = faceit_data.hub_ranking(hub_id=hub_id, return_items=10)
        x = prettytable.PrettyTable(['Player', 'ELO', 'Points', 'Streak', 'Played', "Wins", "Draws", "Losses"])
        for player in ranking["items"]:
            x.add_row([
                player["player"]["nickname"],
                faceit_data.get_player_elo(player['player']['user_id']),
                player["points"],
                player["current_streak"],
                player["played"],
                player["won"],
                player["draw"],
                player["lost"]
            ])
        await message.channel.send(f'```{str(x)}```')

client.run(DISCORD_BOT_TOKEN)