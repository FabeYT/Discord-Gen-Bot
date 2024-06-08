import discord
import os
from discord.ext import commands, tasks
from datetime import datetime, timedelta

Bot_Token = "Bot Token"
prefix = "!"
Status1 = "Status 1"
Status2 = "Status 2"
Status3 = "Status 3"
Name = "DasoFabe Generator"
logoURL = "https://cdn.discordapp.com/attachments/1248399498598813769/1249027409475403897/logostatic.png?ex=6665ceec&is=66647d6c&hm=864ab8bfd0a2d916df00202cd67ddf27c64d65058d0b28d51ef1f83fe60c1259&"
imageURL = "https://cdn.discordapp.com/attachments/1248399498598813769/1249027706075615333/TSvMkES.png?ex=6665cf32&is=66647db2&hm=0fb6f2b52c8fff625be6b107b3c15fe7958e28073d4175f7330263eae60b55e9&"
allowed_channel_id = 1248399498598813769
EmbedColor = discord.Color.blue

# Erstelle eine Instanz der Intents und aktiviere alle Intents
intents = discord.Intents.all()

# Erstelle eine Instanz des Bots
bot = commands.Bot(command_prefix=prefix, intents=intents)

# Dictionary, um die Abkühlzeiten der Benutzer zu speichern
cooldowns = {}

# Liste der Statusnachrichten
status_messages = [Status1, Status2, Status3]

# Event: Bot bereit
@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    change_status.start()  # Startet die Aufgabe zum Ändern des Status

# Hintergrundaufgabe zum Ändern des Status
@tasks.loop(seconds=5)
async def change_status():
    # Wählt zufällig eine Statusnachricht aus der Liste
    status = discord.Game(name=status_messages[change_status.current_loop % len(status_messages)])
    await bot.change_presence(activity=status)

@bot.command(help="Informationen")
async def info(ctx):
    # Erstelle ein Embed
    embed = discord.Embed(title=f'{Name} │ Information', color=EmbedColor())
    
    # Füge die Befehlsliste hinzu
    commands_list = ""
    for command in bot.commands:
        commands_list += f'{bot.command_prefix}{command.name} - {command.help}\n'
        
    embed.add_field(name="Befehle", value=f"```{commands_list}```", inline=False)
    embed.set_image(url=imageURL)
    
    # Füge die Fußzeile hinzu
    embed.set_footer(
        text=f'{ctx.author} │ {datetime.now().strftime("%H:%M:%S")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Füge das Logo hinzu
    embed.set_thumbnail(url=logoURL)
    
    # Sende das Embed
    await ctx.send(embed=embed)

# Event: Auf Erwähnung reagieren
@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        embed = discord.Embed(title="Hallo!", description="Mit dem Befehl `!info` findest du mehr über mich heraus.", color=EmbedColor())
        await message.channel.send(embed=embed)
    await bot.process_commands(message)

# Command: !gen
@bot.command(help="Generate Account")
async def gen(ctx, file_name: str):
    if ctx.channel.id != allowed_channel_id:
        embed = discord.Embed(title='Fehler', description="Dieser Befehl kann nur in einem bestimmten Kanal verwendet werden.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    # Überprüfe die Abkühlzeit
    user_id = ctx.author.id
    now = datetime.now()
    if user_id in cooldowns:
        cooldown_end = cooldowns[user_id]
        if now < cooldown_end:
            remaining_time = cooldown_end - now
            minutes, seconds = divmod(remaining_time.seconds, 60)
            embed = discord.Embed(title="Cooldown", description=f'Bitte warte noch {minutes} Minuten und {seconds} Sekunden bevor du diesen Befehl erneut ausführst.', color=discord.Color.red())
            await ctx.send(embed=embed)
            return
    
    # Setze die neue Abkühlzeit
    cooldowns[user_id] = now + timedelta(minutes=3)
    
    # Ordnername
    folder = 'Accounts'
    
    # Überprüfe, ob der Ordner existiert
    if not os.path.exists(folder):
        await ctx.send(f'Ordner {folder} existiert nicht.')
        return
    
    # Dateipfad
    file_path = os.path.join(folder, f'{file_name}.txt')
    
    # Überprüfe, ob die Datei existiert
    if not os.path.exists(file_path):
        await ctx.send(f'Datei {file_name}.txt existiert nicht.')
        return
    
    # Lies die erste Zeile und lösche sie anschließend
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    if not lines:
        # Erstelle ein Embed mit einer Fehlermeldung
        embed = discord.Embed(title='Fehler', description=f'Keine Accounts mehr für {file_name} verfügbar.', color=discord.Color.red())
        
        # Füge die Fußzeile hinzu
        embed.set_footer(
            text=f'{ctx.author} │ {datetime.now().strftime("%H:%M:%S")}',
            icon_url=ctx.author.display_avatar.url
        )
        
        # Sende das Embed
        await ctx.send(embed=embed)
        return
    
    first_line = lines[0].strip()
    
    # Schreibe die verbleibenden Zeilen zurück in die Datei
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines[1:])
    
    # Erstelle ein Embed für die Account-Daten
    account_embed = discord.Embed(title=f'{Name}', color=EmbedColor())
    account_embed.add_field(name="Account Informationen", value=f'||{first_line}||', inline=False)
    account_embed.set_thumbnail(url=logoURL)
    account_embed.set_image(url=imageURL)
    
    account_embed.set_footer(
        text=f'{ctx.author} │ {datetime.now().strftime("%H:%M:%S")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Sende die Account-Daten per DM als Embed
    try:
        await ctx.author.send(embed=account_embed)
    except discord.Forbidden:
        await ctx.send("Ich kann dir keine DMs senden! Bitte stelle sicher, dass deine DMs aktiviert sind.")
        return
    
    # Bestätigungsnachricht im aktuellen Kanal
    confirmation_embed = discord.Embed(title='Bestätigung', description="Die Account-Daten wurden dir per DM gesendet.", color=discord.Color.green())
    await ctx.send(embed=confirmation_embed)

@bot.command(help="Account Stock")
async def accounts(ctx):
    folder = 'Accounts'
    
    # Überprüfe, ob der Ordner existiert
    if not os.path.exists(folder):
        await ctx.send(f'Ordner {folder} existiert nicht.')
        return
    
    # Durchsuche den Ordner nach .txt-Dateien
    files = [f for f in os.listdir(folder) if f.endswith('.txt')]
    
    if not files:
        await ctx.send('Keine Account-Dateien gefunden.')
        return
    
    # Anzahl der .txt-Dateien
    num_files = len(files)
    
    # Erstelle ein Embed
    embed = discord.Embed(title=f'{Name} Stock │ `{num_files}` Service`s ', color=EmbedColor())
    embed.set_thumbnail(url=logoURL)
    embed.set_image(url=imageURL)
    
    # Füge die Dateinamen und Zeilenanzahl hinzu
    for file in files:
        file_path = os.path.join(folder, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f)
        embed.add_field(name=file.replace('.txt', ''), value=f'{line_count} Accounts', inline=False)
    
    # Füge die Fußzeile hinzu
    embed.set_footer(
        text=f'{ctx.author} │ {datetime.now().strftime("%H:%M:%S")}',
        icon_url=ctx.author.display_avatar.url
    )
    
    # Sende das Embed
    await ctx.send(embed=embed)

bot.run(Bot_Token)
