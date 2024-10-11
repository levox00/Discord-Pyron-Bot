import nextcord
from nextcord import Interaction, ButtonStyle, SlashOption, ui
from nextcord.ext import commands
from nextcord.ui import Button, View
import os
import aiohttp
from datetime import datetime, timedelta, timezone
import sqlite3


intents = nextcord.Intents.default()
intents.invites = True
intents.members = True
base_dir = os.path.dirname(__file__)
bot = commands.Bot(command_prefix="cogs!!", intents=intents)

def create_server_table_if_not_exists(db_path: str, server_id: str):
    # Verbindung zur Datenbank herstellen
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL-Statement für die Erstellung der Tabelle
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS "{server_id}" (
        channel_id TEXT,
        welcome_messages TEXT,
        custom_welcome_message_desc TEXT,
        custom_welcome_message_title TEXT,
        custom_welcome_message_img TEXT,
        role1_id TEXT,
        req_invites1 INTEGER,
        role2_id TEXT,
        req_invites2 INTEGER,
        role3_id TEXT,
        req_invites3 INTEGER,
        role4_id TEXT,
        req_invites4 INTEGER,
        role5_id TEXT,
        req_invites5 INTEGER,
        embed_color TEXT,
        author TEXT,
        author_img_url TEXT,
        author_url TEXT,
        content TEXT,
        join_role_enabled TEXT DEFAULT 'False',
        join_role1 INTEGER DEFAULT NULL,
        join_role2 INTEGER DEFAULT NULL
    )
    """

    # Tabelle erstellen, falls sie nicht existiert
    cursor.execute(create_table_query)

    # Änderungen übernehmen und die Verbindung schließen
    conn.commit()
    conn.close()

    print(f"Table '{server_id}' made or already existed.")
    pass

def get_db_connection():
    db_path = os.path.join(base_dir, "..", 'server_settings.sqlite')  # Ändere den Pfad entsprechend
    conn = sqlite3.connect(db_path)
    return conn

class WelcomeMessageButtons(ui.View):
    def __init__(self):
        super().__init__()

    @ui.button(label="General", style=ButtonStyle.primary)
    async def general_button(self, button: ui.Button, interaction: Interaction):
        await interaction.response.send_modal(GeneralModal())

    @ui.button(label="Author", style=ButtonStyle.secondary)
    async def footer_button(self, button: ui.Button, interaction: Interaction):
        await interaction.response.send_modal(AuthorModal())

    @ui.button(label="Others", style=ButtonStyle.success)
    async def others_button(self, button: ui.Button, interaction: Interaction):
        await interaction.response.send_modal(OthersModal())

class GeneralModal(ui.Modal):
    def __init__(self):
        super().__init__("General Setup")

        self.add_item(ui.TextInput(label="Channel ID", placeholder="Enter the channel ID", required=True))
        self.add_item(ui.TextInput(label="Custom Welcome Message Description", placeholder="'[member]'/[inviter]' to mention the new member/inviter", required=False, max_length=200))
        self.add_item(ui.TextInput(label="Custom Welcome Message Title", placeholder="The custom title", required=False, max_length=50))
        self.add_item(ui.TextInput(label="Custom Message Content", placeholder="The content the embed is attached to", required=False))
    async def callback(self, interaction: Interaction):
        server_id = interaction.guild_id
        db_path = os.path.join(base_dir, "..", "server_settings.sqlite")

        channel_id = self.children[0].value
        desc = self.children[1].value if self.children[1].value else None
        title = self.children[2].value if self.children[2].value else None
        content = self.children[3].value if self.children[3].value else None

        # Erstelle die Tabelle falls sie nicht existiert
        create_server_table_if_not_exists(db_path, server_id)
        
        # Verbinde mit der Datenbank
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(f'SELECT channel_id, custom_welcome_message_desc, custom_welcome_message_title, content FROM "{server_id}" LIMIT 1')
        result = cursor.fetchone()

        current_channel_id =result[0] if result else None
        current_desc = result[1] if result else None
        current_title = result[2] if result else None
        current_content = result[3] if result else None

        # Werte aus den Eingaben holen oder bestehende Werte beibehalten
        channel_id = self.children[0].value if self.children[0].value else current_channel_id
        desc = self.children[1].value if self.children[1].value else current_desc
        title = self.children[2].value if self.children[2].value else current_title
        content = self.children[3].value if self.children[3].value else current_content
        if result:
            # Update des bestehenden Eintrags
            cursor.execute(f"""
            UPDATE "{server_id}"
            SET channel_id = ?, custom_welcome_message_desc = ?, custom_welcome_message_title = ?, content = ?
            WHERE channel_id = ?
            """, (channel_id, desc, title, content, current_channel_id))
        else:
            # Insert eines neuen Eintrags
            cursor.execute(f"""
            INSERT INTO "{server_id}" (channel_id, custom_welcome_message_desc, custom_welcome_message_title, content)
            VALUES (?, ?, ?, ?)
            """, (channel_id, desc, title, content))

        # Änderungen speichern und Datenbankverbindung schließen
        conn.commit()
        conn.close()

        # Bestätigung an den Benutzer
        await interaction.response.send_message("General settings saved!", ephemeral=True)

class AuthorModal(ui.Modal):
    def __init__(self):
        super().__init__("Author Setup")

        self.add_item(ui.TextInput(label="Author", placeholder="Enter author name", required=False))
        self.add_item(ui.TextInput(label="Author Image URL", placeholder="Enter author image URL", required=False))
        self.add_item(ui.TextInput(label="Author URL", placeholder="Enter author URL", required=False))

    async def callback(self, interaction: Interaction):
        server_id = str(interaction.guild_id)  # Server-ID als String für den Tabellennamen
        db_path = os.path.join(base_dir, "..", "server_settings.sqlite")



        # Erstelle die Tabelle falls sie nicht existiert
        create_server_table_if_not_exists(db_path, server_id)
        
        # Verbinde mit der Datenbank
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(f'SELECT author, author_img_url, author_url FROM "{server_id}" LIMIT 1')
        result = cursor.fetchone()

        current_author =result[0] if result else None
        current_author_img_url = result[1] if result else None
        current_author_url = result[2] if result else None

        # Werte aus den Eingaben holen oder bestehende Werte beibehalten
        author = self.children[0].value if self.children[0].value else current_author
        author_img_url = self.children[1].value if self.children[1].value else current_author_img_url
        author_url = self.children[2].value if self.children[2].value else current_author_url
        if result:
            # Update des bestehenden Eintrags
            cursor.execute(f"""
            UPDATE "{server_id}"
            SET author = ?, author_img_url = ?, author_url = ? 
            WHERE author = ?
            """, (author, author_img_url, author_url, current_author))
        else:
            # Insert eines neuen Eintrags
            cursor.execute(f"""
            INSERT INTO "{server_id}" (author, author_img_url, author_url)
            VALUES (?, ?, ?)
            """, (author, author_img_url, author_url))

        # Änderungen speichern und Datenbankverbindung schließen
        conn.commit()
        conn.close()

        # Bestätigung an den Benutzer
        await interaction.response.send_message("Author settings saved!", ephemeral=True)


class OthersModal(ui.Modal):
    def __init__(self):
        super().__init__("Other Settings")

        self.add_item(ui.TextInput(label="Embed Color", placeholder="Enter embed color (hex code)", required=False))
        self.add_item(ui.TextInput(label="Embed Thumbnail", placeholder="Url or [member_avatar]", required=False))

    async def callback(self, interaction: Interaction):
        server_id = str(interaction.guild_id)  # Server-ID als String für den Tabellennamen
        db_path = os.path.join(base_dir, "..", "server_settings.sqlite")

        # Werte aus den Eingaben holen

        # Erstelle die Tabelle falls sie nicht existiert
        create_server_table_if_not_exists(db_path, server_id)
        
        # Verbinde mit der Datenbank
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Prüfen, ob bereits ein Eintrag für diesen Server existiert
        cursor.execute(f'SELECT embed_color, custom_welcome_message_img FROM "{server_id}" LIMIT 1')
        result = cursor.fetchone()

        current_embed_color =result[0] if result else None
        current_embed_thumbnail = result[1] if result else None

        # Werte aus den Eingaben holen oder bestehende Werte beibehalten
        embed_color = self.children[0].value.replace("#", "") if self.children[0].value else current_embed_color
        embed_thumbnail = self.children[1].value if self.children[1].value else current_embed_thumbnail

        try:
            if result:
                # Update des bestehenden Eintrags
                print(f"DEBUG: Updating existing entry for {server_id} with embed_color: {embed_color} and embed_thumbnail: {embed_thumbnail}")
                cursor.execute(f"""
                UPDATE "{server_id}"
                SET embed_color = ?, custom_welcome_message_img = ? WHERE embed_color = ?
                """, (embed_color, embed_thumbnail, current_embed_color))
            else:
                # Insert eines neuen Eintrags
                print(f"DEBUG: Inserting new entry for {server_id} with embed_color: {embed_color} and embed_thumbnail: {embed_thumbnail}")
                cursor.execute(f"""
                INSERT INTO "{server_id}" (embed_color, custom_welcome_message_img)
                VALUES (?, ?)
                """, (embed_color, embed_thumbnail))

            # Änderungen speichern und Datenbankverbindung schließen
            conn.commit()
            await interaction.response.send_message("Other settings saved!", ephemeral=True)
        except sqlite3.Error as e:
            print(f"ERROR: SQLite error: {e}")
        finally:
            conn.close()

        # Bestätigung an den Benutzer

class Join_role_Modal(ui.Modal):
    def __init__(self):
        super().__init__("Other Settings")

        self.add_item(ui.TextInput(label="Role id 1", placeholder="Role id 1 for join role", required=True))
        self.add_item(ui.TextInput(label="Role id 2", placeholder="Role id 2 for join role", required=False))

    async def callback(self, interaction: Interaction):
        server_id = str(interaction.guild_id)  # Server-ID als String für den Tabellennamen
        db_path = os.path.join(base_dir, "server_settings.sqlite")
        guild = interaction.guild

        if interaction.user.id != 1025125432825237514:
            await interaction.response.send_message("No no use this command.", ephemeral=True)

        role1_id = self.children[0].value.replace("<@", "").replace(">", "").replace("&", "")
        role2_id = self.children[1].value.replace("<@", "").replace(">", "").replace("&", "")

        # Überprüfen, ob die Rollen existieren

        role1 = guild.get_role(int(role1_id)) if role1_id.isdigit() else None
        role2 = guild.get_role(int(role2_id)) if role2_id and role2_id.isdigit() else None

        def has_dangerous_permissions(role):
            if role is None:
                return False
            permissions = role.permissions
            return (permissions.administrator or
                    permissions.manage_channels or
                    permissions.manage_roles or
                    permissions.manage_guild or
                    permissions.kick_members or
                    permissions.ban_members or
                    permissions.moderate_members)
        
        if not role1:
                await interaction.response.send_message(f"The role ``{role1_id}`` doesn't exist on this server.", ephemeral=True)
                return

        if role2_id and not role2:
            await interaction.response.send_message(f"The role-id ``{role2_id}`` doesn't exist on this server.", ephemeral=True)
            return

        if has_dangerous_permissions(role1):
            await interaction.response.send_message(f"The role-id {role1_id} has dangerous permissions we do not allow to add these roles as join roles.", ephemeral=True)
            return

        if role2 and has_dangerous_permissions(role2):
            await interaction.response.send_message(f"The role-id {role2_id} has dangerous permissions we do not allow to add these roles as join roles.", ephemeral=True)
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()

        create_server_table_if_not_exists(db_path, server_id)

        # Prüfen, ob bereits ein Eintrag für diesen Server existiert
        cursor.execute(f'SELECT join_role1, join_role2 FROM "{server_id}" LIMIT 1')
        result = cursor.fetchone()

        # Werte für die Join-Rollen setzen
        role1_id = role1.id
        role2_id = role2.id if role2 else None

        try:
            if result:
                # Update des bestehenden Eintrags
                #print(f"DEBUG: Updating existing entry for {server_id} with join_role1: {role1_id} and join_role2: {role2_id}")
                cursor.execute(f"""
                UPDATE "{server_id}"
                SET join_role1 = ?, join_role2 = ?
                """, (role1_id, role2_id))
            else:
                # Insert eines neuen Eintrags
                #print(f"DEBUG: Inserting new entry for {server_id} with join_role1: {role1_id} and join_role2: {role2_id}")
                cursor.execute(f"""
                INSERT INTO "{server_id}" (join_role1, join_role2)
                VALUES (?, ?)
                """, (role1_id, role2_id))

            # Änderungen speichern und Datenbankverbindung schließen
            conn.commit()
            await interaction.response.send_message("Join roles updated!", ephemeral=True)
        except sqlite3.Error as e:
            print(f"ERROR: SQLite error: {e}")
            await interaction.response.send_message(f"Ein Fehler ist aufgetreten: {e}", ephemeral=True)
        finally:
            conn.close()


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    @nextcord.slash_command(description="Set main command.")
    async def set(self, interaction: Interaction):
        pass

    @set.subcommand(name="joinroles", description="Display something about the server.")
    async def autoroles(
        self,
        interaction: Interaction,
        enabled: str = nextcord.SlashOption(description="Enable or disable welcome messages (True/False)", required=True, choices=["True", "False"])
    ):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        else:
            pass
        if interaction.user.guild_permissions.administrator:
            pass
        else:
            await interaction.response.send_message("You need admin perms to use this command.", ephemeral=True)
            return
        server_id = str(interaction.guild_id)
        conn = get_db_connection()
        cursor = conn.cursor()
        db_path = os.path.join(base_dir, "..", "server_settings.sqlite")
        # Sicherstellen, dass die Tabelle existiert
        create_server_table_if_not_exists(db_path, str(interaction.guild_id))
        


        if enabled == "True":
            cursor.execute(f''' 
                UPDATE "{server_id}" SET join_role_enabled = ?
            ''', ("True",))
            await interaction.response.send_modal(Join_role_Modal())
            await interaction.followup.send("Join roles enabled!", ephemeral=True)
            conn.commit()
            conn.close()
        elif enabled == "False":
            try:
                # Prüfen, ob bereits ein Eintrag für diesen Server existiert
                cursor.execute(f'SELECT join_role_enabled FROM "{server_id}" LIMIT 1')
                result = cursor.fetchone()

                if result:
                    # Wenn bereits ein Eintrag existiert, update den bestehenden Eintrag
                    cursor.execute(f'''
                        UPDATE "{server_id}"
                        SET join_role_enabled = ?
                    ''', ("False",))
                else:
                    # Wenn kein Eintrag existiert, insert
                    cursor.execute(f''' 
                        INSERT INTO "{server_id}" (join_role_enabled)
                        VALUES (?)
                    ''', ("False",))
                
                # Bestätige die Änderungen in der Datenbank
                conn.commit()
                await interaction.response.send_message("Join roles disabled!", ephemeral=True)
            except sqlite3.Error as e:
                print(f"ERROR: SQLite error: {e}")
                await interaction.response.send_message("An error occurred while disabling join roles.", ephemeral=True)
            finally:
                conn.close()

    @nextcord.slash_command(description="Display something about the server.")
    async def welcome(self, interaction: Interaction):
        pass

    @welcome.subcommand(name="messages", description="Toggle welcome messages and optionally set a custom welcome message if you choose 'True'")
    async def toggle_welcome(
        self,
        interaction: Interaction,
        toggle: str = nextcord.SlashOption(description="Enable or disable welcome messages (True/False)", required=True, choices=["True", "False"])
    ):
        # Check if the user has admin permissions
        if not any(role.permissions.administrator for role in interaction.user.roles):
            await interaction.send("You need admin perms to use this command.", ephemeral=True)
            return

        # Define database path
        db_path = os.path.join(os.path.dirname(__file__), "..", "server_settings.sqlite")


        # Create the server-specific table if it doesn't exist
        server_id = str(interaction.guild_id)

        if toggle == "True":
            # Create the embed
            embed = nextcord.Embed(
                title="Welcome Message Settings",
                description=(
                    "You can customize the welcome message using the following placeholders:\n"
                    "[member] - to mention the new member\n"
                    "[inviter] - to mention the inviter\n"
                    "[member_avatar] - to show the member's avatar\n"
                    "[server] - to display the server name\n"
                    "[member_count] - to show the number of members in the server"
                ),
                color=nextcord.Color.blue()
            )
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            create_server_table_if_not_exists(db_path, server_id)

            cursor.execute(
                f'UPDATE "{server_id}" SET welcome_messages = ?',
                ("True",)  # Set to 1 for True
            )

            conn.commit() 

            # Send the embed with buttons
            await interaction.response.send_message(embed=embed, view=WelcomeMessageButtons())

        elif toggle == "False":
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Drop the server-specific table to completely remove welcome messages and settings
            cursor.execute(f'DROP TABLE IF EXISTS "{server_id}"')

            # Commit the changes to the database and close the connection
            conn.commit()
            conn.close()

            # Send a confirmation message
            await interaction.response.send_message("Welcome messages have been disabled.", ephemeral=True)

    @nextcord.slash_command(name="avatar", description="Show the banner or icon of a user")
    async def useravatarpfp(self, interaction: nextcord.Interaction, 
                 member: nextcord.Member, 
                 type: str = SlashOption(
                     name="type",
                     description="Choose between avatar or banner",
                     choices={"Avatar": "avatar", "Banner": "banner"},
                     required=True),
                 avatar_type: str = SlashOption(
                     name="avatar_type",
                     description="Choose between server or main avatar",
                     choices={"Main Avatar": "main", "Server Avatar": "server"},
                     required=False)):
        """
        Display a user's avatar or banner. You can choose between the global (main) and the server-specific avatar.
        """
        
        if type == "banner":
            # Überprüfen, ob der Banner des Servers abgerufen werden soll
            if member.id == interaction.guild.owner_id:  # Optional: nur für Serverbesitzer
                server_banner = interaction.guild.banner
                if server_banner:
                    banner_url = f'https://cdn.discordapp.com/banners/{interaction.guild.id}/{server_banner}.png?size=2048'
                    embed = nextcord.Embed(title=f"{interaction.guild.name}'s Banner", color=0x7d89ff)
                    embed.set_image(url=banner_url)
                    embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("Der Server hat keinen Banner gesetzt.")
                return
            
            # API-Anfrage für Benutzerdaten, um den Banner abzurufen
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://discord.com/api/v10/users/{member.id}', 
                                    headers={'Authorization': f'Bot {self.bot.http.token}'}) as response:
                    if response.status == 200:
                        data = await response.json()
                        banner = data.get('banner')
                        
                        if banner:
                            extension = '.gif' if banner.startswith('a_') else '.png'
                            banner_url = f'https://cdn.discordapp.com/banners/{member.id}/{banner}{extension}?size=2048'
                            embed = nextcord.Embed(title=f"{member.display_name}'s Banner", color=0x7d89ff)
                            embed.set_image(url=banner_url)
                            embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
                            await interaction.response.send_message(embed=embed)
                        else:
                            await interaction.response.send_message(f"{member.display_name} has no banner.")
                    else:
                        await interaction.response.send_message("Something went wrong.")
            return
        
        # Logik für Avatare
        if avatar_type == "server" and member.guild_avatar:
            avatar_url = member.guild_avatar.url
            title = f"{member.display_name}'s Avatar"
        else:
            avatar_url = member.display_avatar.url  # Zeigt den globalen Avatar an
            title = f"{member.display_name}'s Avatar"

        # Erstelle einen Embed mit dem Avatar
        embed = nextcord.Embed(title=title, color=0x7d89ff)
        embed.set_image(url=avatar_url)  # Füge das Avatar-Bild hinzu
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(name="server", description="Display something about the server.")
    async def server(self, interaction: nextcord.Interaction):
        pass

    # Befehl, um die Serverstatistiken anzuzeigen
    @server.subcommand(name="stats", description="Show the stats of the server.")
    async def stats(self, interaction: nextcord.Interaction):
        guild = interaction.guild  # Der Server (Guild), in dem der Befehl ausgeführt wird

        # Anzahl der Mitglieder
        total_members = guild.member_count

        # Anzahl der Online-Mitglieder
        online_members = sum(member.status != nextcord.Status.offline for member in guild.members)

        # Anzahl der Rollen
        role_count = len(guild.roles)

        # Anzahl der Channels (Text- und Sprachkanäle)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        total_channels = text_channels + voice_channels

        # Anzahl der Kategorien
        category_count = len(guild.categories)

        # Besitzer des Servers
        owner = guild.owner

        # Boost-Level und Anzahl der Boosts
        boost_tier = guild.premium_tier
        boost_count = guild.premium_subscription_count

        # Erstellungsdatum des Servers (Serveralter)
        created_at = guild.created_at
        timestamp = int(created_at.timestamp())  # Unix-Zeitstempel
        current_time = datetime.now(created_at.tzinfo)  # Stelle sicher, dass beide Zeiten die gleiche Zeitzone haben
        server_age = (current_time - created_at).days 

        # Formatierte Ausgabe
        embed = nextcord.Embed(title=f'Server Stats for **{guild.name}**', color=0x7d89ff)
        embed.set_thumbnail(url=guild.icon.url)  # Server Icon hinzufügen
        embed.add_field(name="Total Members", value=f"{total_members} <:Members:1287442366164238407>", inline=True)
        embed.add_field(name="Online Members", value=f"{online_members} <:Online:1287444292037640284>", inline=True)
        embed.add_field(name="Roles", value=role_count, inline=True)
        embed.add_field(name="Channels", value=total_channels, inline=True)
        embed.add_field(name="Categories", value=category_count, inline=True)
        embed.add_field(name="Owner", value=f"<@{owner.id}>", inline=True)
        embed.add_field(name="Server Boosts", value=f"{boost_count} (Tier **{boost_tier}**)", inline=True)
        embed.add_field(name="Server created at", value=f"<t:{timestamp}:d> (<t:{timestamp}:R>)", inline=True)

        await interaction.response.send_message(embed=embed)

    @server.subcommand(name="icon", description="Shows the icon or banner of a server")
    async def icon(self, interaction: nextcord.Interaction):

        # Für das Server-Icon
        if interaction.guild.icon:
            icon_url = interaction.guild.icon.url
            embed = nextcord.Embed(title=f"{interaction.guild.name}'s Icon", color=0x7d89ff)
            embed.set_image(url=icon_url)
            embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("The server has no icon.")

    @nextcord.slash_command(description="View a list with all the commands")
    async def help(self, interaction: Interaction):
        embed = nextcord.Embed(
            title = "Help",
            description = "This is a list of all commands that are currently available",
            color=0x7d89ff
        )
        embed.add_field(name="General Commands", value="> </help:1287195193463935038> Display this message\n> </avatar:1287490634537635900>\n> </server icon:1287490636986974360> Display the server icon\n> </server stats:1287490636986974360> Display stats about the server")
        embed.add_field(name="Giveaway Commands", value="> </giveaway create:1287195275949244426> Start a giveaway\n> </giveaway reroll:1287195275949244426> Reroll a giveaway", inline=True)
        embed.add_field(name="Invite Commands", value="> </invites:1287490632679555257> Display the invite stats of a single user\n> </leaderboard invites:1287195195590574170> Display the top 10 inviters\n> </inviter:1287195192033542174> Display who invited a selected user\n > </leaderboard export:1287195195590574170> Export the whole leaderboard\n> </leaderboard replace:1287195195590574170> Import a exported leaderboard file\n> </invitelist:1287195190129332307> Display a list of users someone invited", inline=False)
        embed.add_field(name="Config Commands", value="> </invrewards:1287195197209444394>", inline=True)
        await interaction.response.send_message(embed=embed)


def setup(bot): 
    bot.add_cog(Basic(bot))
