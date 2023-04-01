from discord.ext import tasks, commands
from service.faceit_data_api import FaceitData
import prettytable
from pprint import pprint

class MatchWatcher(commands.Cog):
    def __init__(self, bot_channel, hub_id, faceit_data, player_elos):
        self.bot_channel = bot_channel
        self.hub_id = hub_id
        self.watch_ongoing_matches.start()
        self.faceit_data = faceit_data
        self.scoreboard_message = None
        self.player_elos = player_elos

    def cog_unload(self):
        self.watch_ongoing_matches.cancel()

    def get_matches(self):
        return self.faceit_data.hub_matches(hub_id=self.hub_id, type_of_match="ongoing")
    
    def format_tables(self, hub_matches):
        tables = []
        for match_details in hub_matches["items"]:
            team1 = match_details["teams"]["faction1"]
            team2 = match_details["teams"]["faction2"]
            score1 = 0
            score2 = 0
            if "results" in match_details: 
                score1 = match_details["results"]["score"]['faction1']
                score2 = match_details["results"]["score"]['faction2']
            match_title = f'{team1["name"]} {score1} vs {score2} {team2["name"]}'
            print(match_title)

            x = prettytable.PrettyTable([f'{team1["name"]} {score1}', f'{score2} {team2["name"]}'])
            for i, player in enumerate(team1["roster"]):
                x.add_row([f'{player["game_player_name"]} - ELO {self.faceit_data.get_player_elo(player["player_id"])}', f'{team2["roster"][i]["game_player_name"]} - ELO {self.faceit_data.get_player_elo(team2["roster"][i]["player_id"])}'])
            tables.append(str(x))
        return tables

    @tasks.loop(seconds=30)
    async def watch_ongoing_matches(self):
        matches = self.get_matches()
        output_tables = '\n'.join(self.format_tables(matches))
        if self.scoreboard_message is None:
            self.scoreboard_message = await self.bot_channel.send(f'```{output_tables}```')
        else:
            await self.scoreboard_message.edit(content=f'```{output_tables}```')