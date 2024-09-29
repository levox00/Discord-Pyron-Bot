import nextcord
from nextcord import Interaction, ButtonStyle
from nextcord.ext import commands
from nextcord.ui import Button, View
import aiofiles
import sqlite3
import os
import json
import random
from datetime import datetime, timedelta, timezone
import asyncio
import re
import io
from dotenv import load_dotenv
def load_config():
    # Bestimme das Verzeichnis, in dem das aktuelle Skript ausgeführt wird
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Erstelle den Pfad zur config.json basierend auf dem Skript-Verzeichnis
    config_path = os.path.join(script_dir, 'config.json')
    
    # Öffne und lade die config.json-Datei
    with open(config_path, 'r') as f:
        return json.load(f)
    
config = load_config()

BOT_TOKEN = os.getenv('DISCORD_TOKEN')
OWNER = int(config["OWNER_ID"])

intents = nextcord.Intents.default()
intents.invites = True
intents.members = True
intents.presences = True
intents.message_content = True
base_dir = os.path.dirname(__file__)
bot = commands.Bot(command_prefix="py!", intents=intents)

def parse_duration(duration_str: str) -> int:
    """Convert a duration string (e.g., '10s', '10m', '2h', '3d', '1h30m') into seconds."""
    total_seconds = 0
    pattern = re.compile(r"(\d+)([smhd])")
    matches = pattern.findall(duration_str.lower())

    if not matches:
        raise ValueError("Invalid duration format. Use '10s', '10m', '10h', '7d', or combinations like '1h30m'.")

    for value, unit in matches:
        value = int(value)
        if unit == 's':
            total_seconds += value
        elif unit == 'm':
            total_seconds += value * 60
        elif unit == 'h':
            total_seconds += value * 3600
        elif unit == 'd':
            total_seconds += value * 86400
        else:
            raise ValueError("Unsupported duration unit. Use 's', 'm', 'h', or 'd'.")

    # Check if duration exceeds 7 days (604800 seconds)
    max_duration = 7 * 86400  # 7 days in seconds
    if total_seconds > max_duration:
        raise ValueError("Duration exceeds the maximum allowed duration of 7 days.")

    return total_seconds

async def load_json_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)













script_dir = os.path.dirname(os.path.abspath(__file__))
invites_dir = os.path.join(script_dir, 'invites')
cogs_dir = os.path.join(script_dir, "cogs")

if not os.path.exists(cogs_dir):
    os.makedirs(cogs_dir)
if not os.path.exists(invites_dir):
    os.makedirs(invites_dir)
# Funktion zur Verbindung mit der SQLite-Datenbank eines Servers

def get_db_connection(guild_id):
    db_path = os.path.join(script_dir, 'invites', f'{guild_id}_invites.sqlite')
    conn = sqlite3.connect(db_path)
    return conn

def get_invite_db_connection(guild_id):
    db_path = os.path.join(script_dir, 'invites', f'{guild_id}_invites.sqlite')
    conn = sqlite3.connect(db_path)
    return conn

# Funktion zum Erstellen der Tabelle für einen Server, falls sie noch nicht existiert
def ensure_invite_codes_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS invite_codes (
        code TEXT PRIMARY KEY,
        inviter_id INTEGER,
        uses_count INTEGER NOT NULL DEFAULT 0
    );
    ''')
    conn.commit()

# Funktion zum Entfernen alter Invite-Codes für einen Server


# Funktion zum Hinzufügen neuer Invite-Codes
def add_invite_code(conn, code, inviter_id, uses_count):
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO invite_codes (code, inviter_id, uses_count)
                      VALUES (?, ?, ?)
                      ON CONFLICT(code) DO UPDATE SET
                          inviter_id = excluded.inviter_id,
                          uses_count = excluded.uses_count''',
                   (code, inviter_id, uses_count))
    conn.commit()


def create_tables(conn):
    cursor = conn.cursor()
    
    # Tabelle für Einladungsstatistiken erstellen
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS invite_stats (
        inviter_id INTEGER PRIMARY KEY,
        invite_count INTEGER NOT NULL DEFAULT 0,
        leave_count INTEGER NOT NULL DEFAULT 0
    );
    ''')

    # Tabelle für eingeladene Nutzer erstellen
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS invited_users (
        inviter_id INTEGER NOT NULL,
        user_ids TEXT NOT NULL,  -- Speichert die User-IDs der eingeladenen Nutzer
        leave_ids TEXT NOT NULL,  -- Speichert die User-IDs der verlassenen Nutzer
        UNIQUE(inviter_id)
    );
    ''')
    conn.commit()

def replace_text_variables(text, member, inviter_id, guild):
    return (text
            .replace("[member]", member.mention)
            .replace("[inviter]", f"<@{inviter_id}>")
            .replace("[server]", guild.name)
            .replace("[member_count]", str(guild.member_count)))

def replace_image_variables(text, member, guild):
    return (text
            .replace("[member_avatar]", member.display_avatar.url)
            .replace("[server_icon]", guild.icon.url))

@bot.event
async def on_member_join(member):
    guild = member.guild
    server_id = guild.id
    print(f"{member.name} has joined {guild.name}!")

    invites = await guild.invites()

    inviter_id = None
    for invite in invites:
        # Verbindung zur anderen Datenbank, die invite_codes enthält
        invite_codes_conn = get_db_connection(guild.id)  # Diese Funktion sollte die Verbindung zur invite_codes-Datenbank herstellen
        invite_codes_cursor = invite_codes_conn.cursor()

        # Hole die uses_count für den aktuellen Invite aus der anderen Datenbank
        invite_codes_cursor.execute('SELECT uses_count FROM invite_codes WHERE code = ?', (invite.code,))
        invite_data = invite_codes_cursor.fetchone()

        if invite_data and invite.uses > invite_data[0]:
            inviter_id = invite.inviter.id
            break
        
        invite_codes_cursor.close()
        invite_codes_conn.close() 

    if inviter_id:
        print(f"DEBUG: Einladender ID gefunden: {inviter_id}")

        # Hole die Willkommensnachrichteneinstellungen
        server_info_conn = sqlite3.connect('server_settings.sqlite')
        server_info_cursor = server_info_conn.cursor()
        server_info_cursor.execute(f'SELECT channel_id, welcome_messages, custom_welcome_message_desc, custom_welcome_message_title, custom_welcome_message_img, embed_color, author, author_img_url, author_url, content FROM "{server_id}"')
        settings = server_info_cursor.fetchone()

        if settings:
            # print(f"DEBUG: Servereinstellungen gefunden: {settings}")
            channel_id, welcome_messages_enabled, custom_desc, custom_title, custom_img, embed_color, author, author_img_url, author_url, content = settings
            welcome_messages_enabled = settings[1] in ['True', '1'] # Sicherstellen, dass es ein Boolean ist

            channel = guild.get_channel(int(channel_id))

            if channel:
                # print(f"DEBUG: Kanal mit ID {channel_id} gefunden: {channel.name}")
                if welcome_messages_enabled:
                    # Benutzerdefiniertes Embed erstellen
                    embed = nextcord.Embed(
                        title=replace_text_variables(custom_title or f"Welcome to {guild.name}!", member, inviter_id, guild), 
                        description=replace_text_variables(custom_desc or f"{member.mention} joined! They were invited by <@{inviter_id}>.", member, inviter_id, guild),
                        color=0x7d89ff
                        )
                    embed.set_thumbnail(url=replace_image_variables(custom_img or guild.icon.url, member, guild))
                    embed.set_author(name=replace_text_variables(author or "Pyron", member, inviter_id, guild), url=replace_image_variables(author_url or "https://github.com/levox1/Discord-InviteTracker-Bot", member, guild), icon_url=replace_image_variables(author_img_url or "https://cdn.discordapp.com/avatars/1088751762401398865/e795171c56cce3e8199e228136e77eb9.webp?size=1024&animated=true&width=0&height=256", member, guild))
                    embed.color = int(embed_color, 16)
                    emb_content = replace_text_variables(content or f"Welcome {member.mention}!", member, inviter_id, guild)

                    # print(f"DEBUG: Custom Embed: {embed.to_dict()}")
                try:
                    await channel.send(embed=embed, content=emb_content)
                    # print("DEBUG: Embed gesendet.")
                except Exception as e:
                    print(f"ERROR: Fehler beim Senden des Embeds: {e}")

        server_info_cursor.close()
        server_info_conn.close()

        #hier soll die andere datenbank benutzt werden also invite


        db_path = os.path.join(invites_dir, f'{server_id}_invites.sqlite')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Hole die aktuelle Liste der eingeladenen und verlassenen User-IDs
        cursor.execute('SELECT user_ids, leave_ids FROM invited_users WHERE inviter_id = ?', (inviter_id,))
        row = cursor.fetchone()

        if row:
            user_ids = row[0].split(',')
            leave_ids = row[1].split(',')

            # Überprüfen, ob der Benutzer in leave_ids ist
            if str(member.id) in leave_ids:
                leave_ids.remove(str(member.id))
                user_ids.append(str(member.id))

                new_user_ids = ','.join(user_ids)
                new_leave_ids = ','.join(leave_ids)

                cursor.execute('UPDATE invited_users SET user_ids = ?, leave_ids = ? WHERE inviter_id = ?', 
                               (new_user_ids, new_leave_ids, inviter_id))

                cursor.execute('UPDATE invite_stats SET leave_count = leave_count - 1 WHERE inviter_id = ?', (inviter_id,))
            else:
                if str(member.id) not in user_ids:
                    user_ids.append(str(member.id))

                new_user_ids = ','.join(user_ids)
                cursor.execute('UPDATE invited_users SET user_ids = ? WHERE inviter_id = ?', (new_user_ids, inviter_id))
                cursor.execute('UPDATE invite_stats SET invite_count = invite_count + 1 WHERE inviter_id = ?', (inviter_id,))
        else:
            cursor.execute('INSERT INTO invited_users (inviter_id, user_ids, leave_ids) VALUES (?, ?, ?)', 
                           (inviter_id, str(member.id), ''))
            cursor.execute('UPDATE invite_stats SET invite_count = invite_count + 1 WHERE inviter_id = ?', (inviter_id,))

            cursor.execute(''' 
            INSERT INTO invite_stats (inviter_id, invite_count, leave_count) 
            VALUES (?, 1, 0) 
            ON CONFLICT(inviter_id) 
            DO UPDATE SET invite_count = invite_count + 1;
            ''', (inviter_id,))
        
        # Hole den invite_count des Einladers ab
        cursor.execute('SELECT invite_count FROM invite_stats WHERE inviter_id = ?', (inviter_id,))
        invite_count = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if invite_count:
            invite_count = invite_count[0]
            #print(f"DEBUG: Invite Count for {inviter_id}: {invite_count}")

            # Verbindung zur server_infos.sqlite herstellen
            server_info_conn = sqlite3.connect('server_settings.sqlite')
            server_info_cursor = server_info_conn.cursor()

            # Hole die Rollen-Belohnungen aus der server_id-Tabelle
            server_info_cursor.execute(f'SELECT role1_id, req_invites1, role2_id, req_invites2, role3_id, req_invites3, role4_id, req_invites4, role5_id, req_invites5 FROM "{server_id}"')
            rewards = server_info_cursor.fetchone()

            if rewards:
                # Extrahiere die welcome_channel_id und welcome_messages


                for i in range(5):
                    role_id = rewards[i * 2]
                    req_invites = rewards[i * 2 + 1]

                    if role_id and req_invites is not None:
                        #print(f"DEBUG: Checking if the inviters invite count is higher than any of the req_invites {invite_count} >= {req_invites}")
                        if invite_count >= req_invites:
                            role = guild.get_role(int(role_id))
                            if role:
                                inviter = guild.get_member(inviter_id)
                                await inviter.add_roles(role)
                                #print(f"DEBUG: Role {role.name} was added to {inviter.name} for {invite_count} invites.")
                            else:
                                print(f"DEBUG: Role {role_id} not found")


        invite_codes_conn = get_db_connection(guild.id)
        invite_codes_cursor = invite_codes_conn.cursor()

        invite_codes_cursor.execute('UPDATE invite_codes SET uses_count = uses_count + 1 WHERE code = ?', (invite.code,))
        invite_codes_conn.commit()
        invite_codes_conn.close()


# Event, das ausgeführt wird, wenn ein Mitglied den Server verlässt
@bot.event
async def on_member_remove(member):
    guild = member.guild
    print(f"{member.name} has left {guild.name}!")

    conn = get_db_connection(guild.id)
    cursor = conn.cursor()

    # Hole alle Einladenden und deren User-IDs
    cursor.execute('SELECT inviter_id, user_ids, leave_ids FROM invited_users')
    rows = cursor.fetchall()

    user_found = False

    for row in rows:
        inviter_id, user_ids_str, leave_ids_str = row
        user_ids = user_ids_str.split(',')
        leave_ids = leave_ids_str.split(',')

        # Überprüfen, ob die Member-ID in den user_ids ist
        if str(member.id) in user_ids:
            user_found = True
            user_ids.remove(str(member.id))  # Entferne den User von den eingeladenen IDs
            leave_ids.append(str(member.id))  # Füge den User zu den verlassenen IDs hinzu

            # Update die Tabellen
            new_user_ids = ','.join(user_ids)
            new_leave_ids = ','.join(leave_ids)

            cursor.execute('UPDATE invited_users SET user_ids = ?, leave_ids = ? WHERE inviter_id = ?', 
                           (new_user_ids, new_leave_ids, inviter_id))

            # Aktualisiere die Statistiken für den Einladenden
            cursor.execute(''' 
            UPDATE invite_stats SET leave_count = leave_count + 1 
            WHERE inviter_id = ?; 
            ''', (inviter_id,))

            break  # Beende die Schleife, da wir den User gefunden haben

    if user_found:
        conn.commit()  # Änderungen speichern
    conn.close()  # Verbindung schließen

@bot.event
async def on_invite_create(invite):
    #print(f"New invite created: {invite.code} by {invite.inviter.name}!")
    guild = invite.guild
    # Erstelle den Pfad zur Datenbankdatei
    codes_dir = os.path.join(base_dir, 'invites')
    db_path = os.path.join(codes_dir, f"{invite.guild.id}_invites.sqlite")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Füge den neuen Einladungslink zur Datenbank hinzu
    cursor.execute('''
    INSERT INTO invite_codes (code, inviter_id, uses_count) VALUES (?, ?, ?)
    ON CONFLICT(code) DO UPDATE SET
        inviter_id = excluded.inviter_id,
        uses_count = excluded.uses_count;
    ''', (invite.code, invite.inviter.id, invite.uses))

    conn.commit()
    conn.close()

    # print(f"Invite code {invite.code} has been added or updated.")

@bot.event
async def on_guild_join(guild):
    print(f"Bot has been added to {guild.name}!")

    # Erstelle das Verzeichnis, falls es nicht existiert
    codes_dir = os.path.join(base_dir, 'invites')
    os.makedirs(codes_dir, exist_ok=True)

    # Erstelle die Datenbankdatei für die Einladungs-Codes
    db_path = os.path.join(codes_dir, f"{guild.id}_invites.sqlite")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tabelle für Einladungs-Codes erstellen
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS invite_codes (
        code TEXT PRIMARY KEY,
        inviter_id INTEGER NOT NULL,
        uses_count INTEGER NOT NULL
    );
    ''')

    # Hole die aktuellen Einladungen und speichere sie in der Datenbank
    invites = await guild.invites()
    for invite in invites:
        cursor.execute('''
        INSERT OR REPLACE INTO invite_codes (code, inviter_id, uses_count) VALUES (?, ?, ?);
        ''', (invite.code, invite.inviter.id, invite.uses))

    conn.commit()
    conn.close()

    print(f"Invite codes for {guild.name} have been saved.")

@bot.event
async def on_guild_remove(guild):
    print(f"Bot has been removed from {guild.name}!")

    # Pfad zur Einladungs-Codes-Datenbank für den Server
    invites_db_path = os.path.join(base_dir, 'invites', f"{guild.id}_invites.sqlite")
    if os.path.exists(invites_db_path):
        os.remove(invites_db_path)
        print(f"Deleted invite codes database for {guild.name}.")
    else:
        print(f"No invite codes database found for {guild.name}.")

# Event, das ausgeführt wird, wenn der Bot bereit ist
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    await bot.change_presence(
        activity=nextcord.Game(name="/help | Free open source bot!"),
    )
    # Über alle Server iterieren, in denen der Bot ist
    for guild in bot.guilds:
        print(f"Updating invite codes for guild: {guild.name} ({guild.id})")

        # Verbindung zur SQLite-Datenbank des Servers herstellen
        conn = get_db_connection(guild.id)

        # Sicherstellen, dass die Invite-Codes-Tabelle existiert
        ensure_invite_codes_table(conn)

        # Aktuelle Invite-Codes für den Server abrufen
        invites = await guild.invites()

        # Die aktuellen Invite-Codes in die Datenbank einfügen
        for invite in invites:
            code = invite.code
            inviter_id = invite.inviter.id if invite.inviter is not None else None  # Überprüfung, ob inviter None ist
            uses_count = invite.uses

            # Neue Invite-Codes zur Datenbank hinzufügen
            add_invite_code(conn, code, inviter_id, uses_count)

        # Verbindung schließen
        conn.close()

        print(f"Updated invites for guild {guild.name}")

for fn in os.listdir(cogs_dir):
    if fn.endswith(".py"):
        bot.load_extension(f"cogs.{fn[:-3]}")

@bot.command()
async def load(ctx, extension):
    if ctx.author.id != OWNER:
        await ctx.send("You need owner perms to use this command.")
        return
    bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Loaded cog.")

@bot.command()
async def unload(ctx, extension):
    if ctx.author.id != OWNER:
        await ctx.send("You need owner perms to use this command.")
        return
    bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Unloaded cog.")

@bot.command()
async def reload(ctx, extension):
    if ctx.author.id != OWNER:
        await ctx.send("You need owner perms to use this command.")
        return
    bot.reload_extension(f"cogs.{extension}")
    await ctx.send(f"Reloaded cog.")

bot.run(BOT_TOKEN)
