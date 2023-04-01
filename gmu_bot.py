import discord
import prettytable

from service.match_watcher import MatchWatcher
from service.faceit_data_api import FaceitData
from pprint import pprint

DISCORD_BOT_TOKEN=""
FACEIT_API_KEY=""
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

    if message.content == '/stats':
        hub_statistics = faceit_data.hub_statistics(hub_id=hub_id, return_items=10)

        x = prettytable.PrettyTable(["Player", "Win %", "Avg K/R", "Avg K/D", "Avg Kills", "Matches", "Kills", "Deaths", "3K", "4K", "5K"])
        for player in hub_statistics['players']:
            x.add_row([
                player["nickname"],
                player["stats"]["Win Rate %"],
                player["stats"]["Average K/R Ratio"],
                player["stats"]["Average K/D Ratio"],
                player["stats"]["Average Kills"],
                player["stats"]["Matches"],
                player["stats"]["Kills"],
                player["stats"]["Deaths"],
                player["stats"]["Triple Kills"],
                player["stats"]["Quadro Kills"],
                player["stats"]["Penta Kills"]
            ])

        await message.channel.send(f'```{str(x)}```')

    if message.content.startswith('/stats '):
        player_nickname = message.content.split(" ")[1]
        player_id = faceit_data.player_details(nickname=player_nickname, game="csgo")['player_id']
        player_stats = faceit_data.player_stats(player_id=player_id, game_id="csgo")

        player_elo = faceit_data.get_player_elo(player_id=player_id)

        most_played = sorted(player_stats['segments'], key=lambda d: int(d['stats']['Rounds']))[-1]['label']
        highest_winrate = sorted(player_stats['segments'], key=lambda d: int(d['stats']['Win Rate %']))[-1]['label']
        best_k_r = sorted(player_stats['segments'], key=lambda d: float(d['stats']['Average K/R Ratio']))[-1]['label']
        highest_headshot = sorted(player_stats['segments'], key=lambda d: float(d['stats']['Average Headshots %']))[-1]['label']

        avg_k_d = player_stats['lifetime']['Average K/D Ratio']
        avg_headshot = player_stats['lifetime']['Average Headshots %']
        win_rate = player_stats['lifetime']["Win Rate %"]
        total_wins = player_stats['lifetime']['Wins']
        pprint(player_stats)

        x = prettytable.PrettyTable(["Player", "ELO", "Avg K/D", "Avg HS", "Win Rate", "Wins"])
        x.add_row([player_nickname, player_elo, avg_k_d, avg_headshot, win_rate, total_wins])

        x2 = prettytable.PrettyTable(["Most Played", "Best Win %", "Best K/R", "Best HS"])
        x2.add_row([most_played, highest_winrate, best_k_r, highest_headshot])


        out = '\n'.join([str(x), str(x2)])

        await message.channel.send(f'```{out}```')


client.run(DISCORD_BOT_TOKEN)