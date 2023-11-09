import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone

# Ustawienia intencji w celu uzyskania dostępu do informacji o członkach serwera
intents = discord.Intents.default()
intents.members = True

# Inicjalizacja bota
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command("help")  # Usunięcie domyślnej komendy help

# Komenda help
@bot.command()
async def help(ctx):
    await ctx.send("Usage: sending reminders to verify yourself")

# Event on_ready - wywoływany po zalogowaniu bota
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_verification.start()  # Rozpoczęcie zadania cyklicznego

# Zadanie cykliczne sprawdzające weryfikację użytkowników (co 24 godziny)
@tasks.loop(hours=24)
async def check_verification():
    try:
        guild_id = 1172249999966197775
        guild = bot.get_guild(guild_id)

        if guild is None:
            print(f'Nie udało się znaleźć serwera o ID: {guild_id}')
            return

        # Iteracja przez listę członków serwera
        for member in guild.members:
            join_date = member.joined_at

            if join_date is not None:
                # Konwersja do strefy czasowej UTC
                join_date_utc = join_date.replace(tzinfo=timezone.utc) if join_date.tzinfo is None else join_date.astimezone(timezone.utc)

                # Sprawdzenie, czy minęło 30 dni od dołączenia
                if (datetime.utcnow().replace(tzinfo=timezone.utc) - join_date_utc) >= timedelta(minutes=5):
                    # Sprawdzenie, czy użytkownik nie ma roli "weryfikacja" i nie jest botem
                    is_verified = any(role.name.lower() == 'weryfikacja' for role in member.roles)
                    is_bot = member.bot

                    if not is_verified and not is_bot:
                        # Wysłanie wiadomości prywatnej do użytkownika
                        try:
                            await member.send(
                                'Cześć! Zauważyliśmy, że od pewnego czasu jesteś na Discord Hackerspace Trójmiasto, ale jak do tej pory nie akceptujesz naszego regulaminu. '
                                'Aby zaakceptować regulamin (widoczny na kanale #cześć), wystarczy wejść na kanał #weryfikacja i wysłać wiadomość o treści "t". '
                                'Niedługo będziemy usuwać wszystkie niezweryfikowane osoby, więc jeśli chcesz być częścią społeczności Hackerspace Trójmiasto, zweryfikuj się już teraz. '
                                'Dzięki 🙂'
                            )
                        except discord.HTTPException as e:
                            print(f'Wystąpił błąd podczas wysyłania wiadomości prywatnej do {member}: {e}')

    except Exception as e:
        print(f'Wystąpił błąd w funkcji check_verification: {e}')

# Event on_member_join - wywoływany po dołączeniu nowego członka
@bot.event
async def on_member_join(member):
    print(f'{member} dołączył do serwera.')

# Uruchamianie bota
bot.run('TOKEN_BOTA')