# faceit-discord-bot

## Dependencies:

`python3 -m pip install -r requirements.txt`

## Configuration:

Create a Faceit App in the [Developer App Studio](https://developers.faceit.com/apps)

Copy the server api key into: `FACEIT_API_KEY`

Create a [discord application](https://discord.com/developers/applications) and bot

Copy the bot token into: `DISCORD_BOT_TOKEN`

Set `BOT_CHANNEL_NAME` to channel in your discord server you want bot to print to

Use discord's OAuth link to add the bot to your server:

ie: https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&scope=bot&permissions=534723819584

## Running the bot:

`python3 gmu_bot.py`
