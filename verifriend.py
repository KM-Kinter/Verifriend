import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone
import logging

# Setting up intents to access server member information
intents = discord.Intents.default()
intents.members = True

# Initializing the bot
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command("help")  # Removing the default help command

# Setting up the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('verification_bot')

# Bot token and role name for verification
bot_token = None
verification_role_name = None
guild_id = None
channel_id = None
removal_channel_id = None

# Help command
@bot.command()
async def help(ctx):
    await ctx.send("Usage: sending reminders to verify yourself")


# Event on_ready - triggered upon bot login
@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name}')
    check_verification.start()  # Starting the periodic task


# Function to set token, role name, server ID, channel ID, and removal channel ID
def set_credentials():
    global bot_token, verification_role_name, guild_id, channel_id, removal_channel_id
    bot_token = input('Enter bot token: ')
    verification_role_name = input('Enter verification role name: ')
    guild_id = int(input('Enter guild ID: '))
    channel_id = int(input('Enter channel ID: '))
    removal_channel_id = int(input('Enter removal channel ID: '))


# Periodic task checking user verification
@tasks.loop(hours=24)
async def check_verification():
    try:
        guild = bot.get_guild(guild_id)

        if guild is None:
            logger.error(f'Failed to find a server with ID: {guild_id}')
            return

        verification_role = discord.utils.get(guild.roles, name=verification_role_name)
        removal_channel = bot.get_channel(removal_channel_id)

        # Iterating through the server's member list
        for member in guild.members:
            join_date = member.joined_at

            if join_date is not None:
                join_date_utc = join_date.replace(
                    tzinfo=timezone.utc) if join_date.tzinfo is None else join_date.astimezone(timezone.utc)
                days_since_join = (datetime.utcnow().replace(tzinfo=timezone.utc) - join_date_utc).days

                if days_since_join == 30:
                    try:
                        await member.send(
                                'Cześć! Zauważyliśmy, że od pewnego czasu jesteś na Discord Hackerspace Trójmiasto, ale jak do tej pory nie akceptujesz naszego regulaminu. '
                                'Aby zaakceptować regulamin (widoczny na kanale #cześć), wystarczy wejść na kanał #weryfikacja i wysłać wiadomość o treści "t". '
                                'Niedługo będziemy usuwać wszystkie niezweryfikowane osoby, więc jeśli chcesz być częścią społeczności Hackerspace Trójmiasto, zweryfikuj się już teraz. '
                                'Dzięki 🙂'
                            )
                    except discord.HTTPException as e:
                        logger.warning(f'Error sending a private message to {member}: {e}')

                if days_since_join == 45:
                    try:
                        await member.send(
                                'Cześć! Zauważyliśmy, że od pewnego czasu jesteś na Discord Hackerspace Trójmiasto, ale jak do tej pory nie akceptujesz naszego regulaminu. '
                                'Aby zaakceptować regulamin (widoczny na kanale #cześć), wystarczy wejść na kanał #weryfikacja i wysłać wiadomość o treści "t". '
                                'Za 15 dni będziemy usuwać wszystkie niezweryfikowane osoby, więc jeśli chcesz być częścią społeczności Hackerspace Trójmiasto, zweryfikuj się już teraz. '
                                'Dzięki 🙂'
                            )
                    except discord.HTTPException as e:
                        logger.warning(f'Error sending a private message to {member}: {e}')

                if days_since_join == 54:
                    try:
                        await removal_channel.send(
                            f'{member.mention} will be removed in 6 hours due to lack of verification.'
                        )
                    except discord.HTTPException as e:
                        logger.error(f'Error sending a message: {e}')

                if days_since_join == 60:
                    try:
                        await removal_channel.send(
                            f'Member {member} has been removed due to lack of verification after 60 days.'
                        )
                        await member.kick(reason='Not verified within 60 days')
                    except discord.HTTPException as e:
                        logger.error(f'Error sending a message or kicking {member}: {e}')
                    else:
                        try:
                            await removal_channel.send(
                                f'Member {member} has been removed from the server.'
                            )
                        except discord.HTTPException as e:
                            logger.error(f'Error sending a message: {e}')

        await remove_unverified_members(guild, verification_role)  # Remove unverified members after 60 days

    except Exception as e:
        logger.error(f'Error in the check_verification function: {e}')


# Running the bot
if __name__ == "__main__":
    set_credentials()
    if bot_token:
        bot.run(bot_token)
    else:
        logger.error('Bot token is missing. Please provide the bot token.')
