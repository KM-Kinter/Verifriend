import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone
from dotenv import load_dotenv
import logging
import os

load_dotenv()

# Setting up intents to access server member information
intents = discord.Intents.default()
intents.members = True

# Initializing the bot
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command("help")  # Removing the default help command

# Setting up the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('verification_bot')

# Bot token and dry-run mode from environment variables
discord_token = os.getenv("DISCORD_TOKEN")
dry_run = os.getenv("DRY_RUN") == "True"

if discord_token is None:
    logger.error('Bot token is missing. Please provide the bot token.')
    exit()

# Retrieving other required environment variables
verification_role_name = os.getenv("VERIFICATION_ROLE_NAME")
warn1_role_name = os.getenv("WARN1_ROLE_NAME")
warn2_role_name = os.getenv("WARN2_ROLE_NAME")
guild_id = int(os.getenv("GUILD_ID"))
removal_channel_id = int(os.getenv("REMOVAL_CHANNEL_ID"))

@bot.command()
async def help(ctx):
    await ctx.send("Usage: sending reminders to verify yourself")

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name} (Dry-run: {dry_run})')
    check_verification.start()

@tasks.loop(hours=24)
async def check_verification():
    try:
        guild = bot.get_guild(guild_id)
        if guild is None:
            logger.error(f'Failed to find a server with ID: {guild_id}')
            return

        warn1_role = discord.utils.get(guild.roles, name=warn1_role_name)
        warn2_role = discord.utils.get(guild.roles, name=warn2_role_name)
        removal_channel = bot.get_channel(removal_channel_id)

        for member in guild.members:
            if member.bot or any(role.name != verification_role_name for role in member.roles):
                continue

            join_date = member.joined_at or datetime.utcnow()
            join_date_utc = join_date.replace(tzinfo=timezone.utc)
            days_since_join = (datetime.utcnow().replace(tzinfo=timezone.utc) - join_date_utc).days

            if days_since_join == 30 and warn1_role not in member.roles:
                await add_warning(member, warn1_role, "warn1", removal_channel)
            elif days_since_join == 45 and warn2_role not in member.roles:
                await add_warning(member, warn2_role, "warn2", removal_channel)
            elif days_since_join >= 60 and warn2_role in member.roles:
                await remove_member(member, removal_channel)

    except Exception as e:
        logger.error(f'Error in the check_verification function: {e}')

async def add_warning(member, role, warning_level, channel):
    try:
        await member.send(get_warning_message(warning_level))
        if not dry_run:
            await member.add_roles(role)
        await channel.send(embed=create_embed(member, f"{warning_level.upper()} warning issued"))
    except discord.HTTPException as e:
        logger.error(f'Failed to send warning message or add role to {member}: {e}')

async def remove_member(member, channel):
    if dry_run:
        logger.info(f'[Dry-run] Would remove member {member} ({member.id}) for not verifying within 60 days.')
    else:
        try:
            await channel.send(embed=create_embed(member, "Member removal"))
            await member.kick(reason='Not verified within 60 days')
        except discord.HTTPException as e:
            logger.error(f'Failed to kick {member}: {e}')

def get_warning_message(warning_level):
    return (
        'Cześć! Zauważyliśmy, że od pewnego czasu jesteś na Discord Hackerspace Trójmiasto, ale jak do tej pory nie akceptujesz naszego regulaminu. '
        'Aby zaakceptować regulamin (widoczny na kanale #cześć), wystarczy wejść na kanał #weryfikacja i wysłać wiadomość o treści "t". '
        'Otrzymujesz ostrzeżenie ' + warning_level + '. Niedługo będziemy usuwać wszystkie niezweryfikowane osoby, więc jeśli chcesz być częścią społeczności Hackerspace Trójmiasto, zweryfikuj się już teraz. '
        'Dzięki 🙂'
    )

async def create_embed(member, title):
    embed = discord.Embed(title=title, color=0xFF5733)
    embed.add_field(name="Username", value=f'{member}', inline=True)
    embed.add_field(name="User ID", value=f'{member.id}', inline=True)
    join_date = member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "Unknown"
    embed.add_field(name="Join Date", value=join_date, inline=True)
    return embed

if __name__ == "__main__":
    verification_role_name = os.getenv('VERIFICATION_ROLE_NAME')
    warn1_role_name = os.getenv('WARN1_ROLE_NAME')
    warn2_role_name = os.getenv('WARN2_ROLE_NAME')
    guild_id = int(os.getenv('GUILD_ID'))
    removal_channel_id = int(os.getenv('REMOVAL_CHANNEL_ID'))

    if discord_token:
        bot.run(discord_token)
    else:
        logger.error('Bot token is missing. Please provide the bot token.')