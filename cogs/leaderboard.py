import nextcord
from nextcord import Interaction, ButtonStyle
from nextcord.ext import commands
from nextcord.ui import Button, View
import sqlite3
import os
from datetime import datetime, timedelta, timezone
import asyncio
import json
import aiofiles
import io

script_dir = os.path.dirname(os.path.abspath(__file__))
invite_codes_dir = os.path.join(script_dir, "..", 'invite-codes')
invites_dir = os.path.join(script_dir, "..", 'invites')
if not os.path.exists(invite_codes_dir):
    os.makedirs(invite_codes_dir)
if not os.path.exists(invites_dir):
    os.makedirs(invites_dir)

async def load_json_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def get_invite_db_connection(guild_id):
    db_path = os.path.join(script_dir, "..",  'invites', f'{guild_id}_invites.sqlite')
    conn = sqlite3.connect(db_path)
    return conn

def save_role_rewards(server_id, role_rewards):
    file_path = os.path.join(os.path.dirname(__file__), "..",  "invite_roles", f"{server_id}.json")
    with open(file_path, 'w') as f:
        json.dump(role_rewards, f, indent=4)

def ensure_dir_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)






class InviteLeaderboardView(nextcord.ui.View):
    def __init__(self, guild, start_idx=0, step=10):
        super().__init__()
        self.guild = guild
        self.start_idx = start_idx
        self.step = step
        self.last_interaction_time = nextcord.utils.utcnow()  # Setze die Zeit des letzten Interactions auf die aktuelle Zeit
        self.timer_task = None  # Timer-Task für das Entfernen der View
        self.message = None  # Nachricht, in der die View angezeigt wird
        self.reset_timer()  # Timer starten

    async def fetch_leaderboard(self):
        base_dir = os.path.dirname(__file__)
        db_path = os.path.join(base_dir, "..",  "invites", f"{self.guild.id}_invites.sqlite")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(""" 
            SELECT inviter_id, invite_count, leave_count
            FROM invite_stats
            ORDER BY (invite_count - leave_count) DESC
            LIMIT ? OFFSET ?
        """, (self.step, self.start_idx))
        leaderboard = cursor.fetchall()
        conn.close()
        return leaderboard

    async def update_leaderboard(self, interaction):
        leaderboard = await self.fetch_leaderboard()
        if not leaderboard:
            await interaction.response.send_message("No more inviters.", ephemeral=True)
            return

        embed = nextcord.Embed(title="**Invite Leaderboard**", color=nextcord.Color.blue())
        description = ""
        for i, (inviter_id, total_invite_count, leave_count) in enumerate(leaderboard, start=self.start_idx + 1):
            net_invites = total_invite_count - leave_count
            description += f"> **{i}**. <@{inviter_id}> • **{net_invites}** Invites [ {total_invite_count} Total Invites | {leave_count} Leaves ]\n"
        
        embed.set_thumbnail(url=self.guild.icon.with_size(64))
        embed.set_footer(text="Pyron", icon_url="https://cdn.discordapp.com/avatars/1088751762401398865/e795171c56cce3e8199e228136e77eb9.webp?size=1024&format=webp&width=0&height=256")
        embed.description = description

        # Dynamische Umbenennung der Buttons basierend auf der aktuellen Seite
        prev_label = f"Previous {self.start_idx + 1}-{self.start_idx + self.step}"
        next_label = f"Next {self.start_idx + self.step + 1}-{self.start_idx + 2 * self.step}"

        self.children[0].label = prev_label
        self.children[1].label = next_label
        
        self.children[0].disabled = self.start_idx == 0  # Disable previous button if at the start
        next_batch_exists = len(leaderboard) == self.step  # Prüfe, ob es noch genug Einträge für eine nächste Seite gibt
        self.children[1].disabled = not next_batch_exists  # Deaktiviere den "Next"-Button, wenn es keine weiteren gibt

        if self.message:
            await self.message.edit(embed=embed, view=self)
        else:
            self.message = await interaction.response.send_message(embed=embed, view=self)
        
        self.reset_timer()  # Timer zurücksetzen

    async def remove_view_after_delay(self):
        while True:
            if self.last_interaction_time:
                time_since_last_interaction = (nextcord.utils.utcnow() - self.last_interaction_time).total_seconds()
                if time_since_last_interaction >= 20:
                    try:
                        await self.message.edit(view=None)
                    except nextcord.HTTPException:
                        pass
                    break
            await asyncio.sleep(1)

    def reset_timer(self):
        if self.timer_task:
            self.timer_task.cancel()
        self.timer_task = asyncio.create_task(self.remove_view_after_delay())  # Timer starten

    @nextcord.ui.button(label="Previous", style=nextcord.ButtonStyle.secondary, disabled=True)
    async def previous(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.start_idx >= self.step:
            self.start_idx -= self.step
        else:
            self.start_idx = 0

        self.last_interaction_time = nextcord.utils.utcnow()  # Timer zurücksetzen
        await self.update_leaderboard(interaction)

    @nextcord.ui.button(label="Next", style=nextcord.ButtonStyle.primary)
    async def next(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.start_idx += self.step
        self.last_interaction_time = nextcord.utils.utcnow()  # Timer zurücksetzen
        await self.update_leaderboard(interaction)

class InviteListView(nextcord.ui.View):
    def __init__(self, user, inviter_id, start_idx=0, step=15):
        super().__init__()
        self.user = user
        self.inviter_id = inviter_id
        self.start_idx = start_idx
        self.step = step
        self.last_interaction_time = nextcord.utils.utcnow()  # Setze die Zeit des letzten Interactions auf die aktuelle Zeit
        self.timer_task = None  # Timer-Task für das Entfernen der View
        self.message = None  # Nachricht, in der die View angezeigt wird
        self.reset_timer()  # Timer starten

    async def fetch_invites(self):
        base_dir = os.path.dirname(__file__)
        db_path = os.path.join(base_dir, "..",  "invites", f"{self.user.guild.id}_invites.sqlite")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_ids
            FROM invited_users
            WHERE inviter_id = ?
        """, (self.inviter_id,))
        invited_users = cursor.fetchall()
        conn.close()
        return invited_users

    async def update_invite_list(self, interaction):
        invited_users = await self.fetch_invites()
        if not invited_users:
            await interaction.response.send_message("No more invited users.", ephemeral=True)
            return

        invited_users_str = invited_users[0][0]  # Nimm den ersten Eintrag
        invited_users_list = invited_users_str.split(",")  # Aufteilen in eine Liste

        # Begrenze die Anzahl der angezeigten IDs
        displayed_users = invited_users_list[self.start_idx:self.start_idx + self.step]
        invited_users_mentions = [f"<@{user_id.strip()}>" for user_id in displayed_users]  # IDs formatieren

        embed = nextcord.Embed(
            title=f"Users invited by {self.user.display_name}:",
            description="\n".join(invited_users_mentions),
            color=0x7d89ff
        )
        embed.set_thumbnail(url=self.user.avatar.with_size(64))
        embed.set_footer(text="Pyron", icon_url="https://cdn.discordapp.com/avatars/1088751762401398865/e795171c56cce3e8199e228136e77eb9.webp?size=1024&format=webp&width=0&height=256")

        # Buttons aktivieren oder deaktivieren
        self.children[0].disabled = self.start_idx == 0  # Deaktiviere Previous-Button, wenn am Anfang
        self.children[1].disabled = self.start_idx + self.step >= len(invited_users_list)  # Deaktiviere Next-Button, wenn keine weiteren Einträge vorhanden

        await interaction.response.edit_message(embed=embed, view=self)

    async def remove_view_after_delay(self):
        await asyncio.sleep(20)  # Warte 10 Sekunden
        await self.message.edit(view=None)  # Entferne die Buttons

    def reset_timer(self):
        if self.timer_task:
            self.timer_task.cancel()
        self.timer_task = asyncio.create_task(self.remove_view_after_delay())  # Timer starten

    @nextcord.ui.button(label="Previous", style=nextcord.ButtonStyle.secondary, disabled=True)
    async def previous_15(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.start_idx >= self.step:
            self.start_idx -= self.step
        await self.update_invite_list(interaction)
        self.reset_timer()  # Timer zurücksetzen

    @nextcord.ui.button(label="Next", style=nextcord.ButtonStyle.primary)
    async def next_15(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.start_idx += self.step
        await self.update_invite_list(interaction)
        self.reset_timer()  # Timer zurücksetzen

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="invrewards", description="Set up to 5 invite role rewards")
    async def invrewards(
        self,
        interaction: Interaction,
        role1: str = nextcord.SlashOption(description="Reward Role 1 (ID)", required=True),
        req_invites1: int = nextcord.SlashOption(description="Required invites for reward role 1", required=True),
        role2: str = nextcord.SlashOption(description="Reward Role 2 (ID)", required=False),
        req_invites2: int = nextcord.SlashOption(description="Required invites for reward role 2", required=False),
        role3: str = nextcord.SlashOption(description="Reward Role 3 (ID)", required=False),
        req_invites3: int = nextcord.SlashOption(description="Required invites for reward role 3", required=False),
        role4: str = nextcord.SlashOption(description="Reward Role 4 (ID)", required=False),
        req_invites4: int = nextcord.SlashOption(description="Required invites for reward role 4", required=False),
        role5: str = nextcord.SlashOption(description="Reward Role 5 (ID)", required=False),
        req_invites5: int = nextcord.SlashOption(description="Required invites for reward role 5", required=False)
    ):
        # Check if the user has admin permissions
        if not any(role.permissions.administrator for role in interaction.user.roles):
            await interaction.send("You need admin perms to use this command.", ephemeral=True)
            return
        
    # Clean up role strings
        roles_and_invites = [
            (role1, req_invites1, "role1_id", "req_invites1"),
            (role2, req_invites2, "role2_id", "req_invites2"),
            (role3, req_invites3, "role3_id", "req_invites3"),
            (role4, req_invites4, "role4_id", "req_invites4"),
            (role5, req_invites5, "role5_id", "req_invites5")
        ]
        
        # Strip unwanted characters from roles
        for i, (role, invites, role_column, invites_column) in enumerate(roles_and_invites):
            if role is not None:
                roles_and_invites[i] = (role.replace("<@&", "").replace(">", ""), invites, role_column, invites_column)


        # Define database path
        db_path = os.path.join(os.path.dirname(__file__), "..", "server_settings.sqlite")
        
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create the server-specific table if it doesn't exist
        server_id = str(interaction.guild_id)
        cursor.execute(f"""
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
            footer_author TEXT,
            footer_img_url TEXT,
            footer_url TEXT
        )
        """)
        for role, invites, role_column, invites_column in roles_and_invites:
            if role is not None and invites is not None:
                cursor.execute(f"""
                UPDATE "{server_id}"
                SET {role_column} = ?, {invites_column} = ?
                """, (role, invites))
            

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        await interaction.send("Invite role rewards have been updated.", ephemeral=True)

    @nextcord.slash_command(description="Display a list of who joined by a selected user")
    async def invitelist(self, interaction: Interaction, user: nextcord.Member):
        server_id = interaction.guild.id
        base_dir = os.path.dirname(__file__)
        db_path = os.path.join(base_dir, "..",  "invites", f"{server_id}_invites.sqlite")

        if not os.path.exists(db_path):
            await interaction.send("Invites file not found.", ephemeral=True)
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_ids
            FROM invited_users
            WHERE inviter_id = ?
        """, (user.id,))
        invited_users = cursor.fetchall()
        conn.close()

        if invited_users:
            # Nimm die kommagetrennte Liste und teile sie auf
            invited_users_str = invited_users[0][0]  # Nimm den ersten Eintrag
            invited_users_list = invited_users_str.split(",")  # Aufteilen in eine Liste
            invited_users_list = invited_users_list[:15] 
            invited_users_mentions = [f"<@{user_id.strip()}>" for user_id in invited_users_list]  # IDs formatieren

            if len(invited_users_list) > 14:
                invited_users_mentions.append("...click `Next` to see more")
            embed = nextcord.Embed(
                title=f"Users invited by {user.display_name}:",
                description="\n".join(invited_users_mentions),
                color=0x7d89ff
            )
            embed.set_thumbnail(url= user.avatar.with_size(64))
            embed.set_footer(text="Pyron", icon_url="https://cdn.discordapp.com/avatars/1088751762401398865/e795171c56cce3e8199e228136e77eb9.webp?size=1024&format=webp&width=0&height=256")
            view = InviteListView(user=user, inviter_id=user.id)
            message = await interaction.send(embed=embed, view=view)
            view.message = message  # Speichere die Nachricht für spätere Änderungen
            view.reset_timer()  # Timer starten
        else:
            await interaction.send(f"No invite data found for {user.mention}.", ephemeral=True)

    @nextcord.slash_command(description="Display who invited a selected user")
    async def inviter(self, interaction: Interaction, user: nextcord.Member):
        server_id = interaction.guild.id
        base_dir = os.path.dirname(__file__)
        db_path = os.path.join(base_dir, "..",  "invites", f"{server_id}_invites.sqlite")

        # Check if the SQLite file exists
        if not os.path.exists(db_path):
            await interaction.send("No invitation data found for this server.", ephemeral=True)
            return

        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query to find the inviter based on the user ID
        cursor.execute(""" 
            SELECT inviter_id
            FROM invited_users
            WHERE user_ids LIKE ?
        """, (f"%{user.id}%",))

        result = cursor.fetchone()
        conn.close()

        # Check if an inviter was found
        if result is None:
            await interaction.send(f"The user {user.mention} was not found in the invitation data.", ephemeral=True)
        else:
            inviter_id = result[0]
            inviter_member = interaction.guild.get_member(int(inviter_id))
            
            if inviter_member:
                embed = nextcord.Embed(
                    description=f"{user.mention} was invited by <@{inviter_member.id}>",
                    color=0x7d89ff
                )
                embed.set_thumbnail(url= inviter_member.avatar.with_size(64))
                embed.set_author(name="Pyron", icon_url="https://cdn.discordapp.com/avatars/1088751762401398865/e795171c56cce3e8199e228136e77eb9.webp?size=1024&format=webp&width=0&height=256")
                await interaction.send(embed=embed)
            else:
                embed = nextcord.Embed(
                    description=f"{user.mention} was invited by <@{inviter_id}>, who is no longer on the server",
                    color=0x7d89ff
                )
                embed.set_thumbnail(url= inviter_member.avatar.with_size(64))
                embed.set_author(name="Pyron", icon_url="https://cdn.discordapp.com/avatars/1088751762401398865/e795171c56cce3e8199e228136e77eb9.webp?size=1024&format=webp&width=0&height=256")
                await interaction.send(embed=embed)

    @nextcord.slash_command(description="main command")
    async def leaderboard(self, interaction: Interaction):
        pass


    @leaderboard.subcommand(description="Replace the leaderboard")
    async def replace(self, interaction: Interaction, file: nextcord.Attachment):
        if not any(role.permissions.administrator for role in interaction.user.roles):
            await interaction.send("You need admin perms to use this command.", ephemeral=True)
            return

        server_id = interaction.guild.id
        base_dir = os.path.dirname(__file__)
        invites_directory = os.path.join(base_dir, "..",  "invites")
        db_invites = os.path.join(invites_directory, f"{server_id}_invites.sqlite")

        if not file.filename.endswith(".txt"):
            await interaction.send("Only .txt files are supported!", ephemeral=True)
            return

        # Lese die hochgeladene Datei
        uploaded_file_data = await file.read()
        lines = uploaded_file_data.decode('utf-8').strip().splitlines()

        # Verbinde zur SQLite-Datenbank
        conn_invites = sqlite3.connect(db_invites)
        cursor = conn_invites.cursor()

        # Leere alle Tabellen
        cursor.execute("DELETE FROM invite_stats")
        cursor.execute("DELETE FROM invited_users")

        # Importiere Daten aus der Datei
        current_table = None
        for line in lines:
            if line == "invite_stats":
                current_table = "invite_stats"
                continue
            elif line == "invited_users":
                current_table = "invited_users"
                continue

            if current_table is None or not line:
                continue

            parts = line.split(',')
            if current_table == "invite_stats" and len(parts) == 3:
                cursor.execute("""
                    INSERT INTO invite_stats (inviter_id, invite_count, leave_count)
                    VALUES (?, ?, ?)
                """, (parts[0], int(parts[1]), int(parts[2])))
            elif current_table == "invited_users" and len(parts) == 3:
                cursor.execute("""
                    INSERT INTO invited_users (inviter_id, user_ids, leave_ids)
                    VALUES (?, ?, ?)
                """, (parts[0], parts[1], parts[2]))

        conn_invites.commit()
        conn_invites.close()

        embed = nextcord.Embed(title="Success", description="Your leaderboard has been updated!", color=nextcord.Color.green())
        await interaction.send(embed=embed)




    @leaderboard.subcommand(description="Export the leaderboard")
    async def export(self, interaction: Interaction):
        if not any(role.permissions.administrator for role in interaction.user.roles):
            await interaction.send("You need admin perms to use this command.", ephemeral=True)
            return
        
        server_id = interaction.guild.id
        base_dir = os.path.dirname(__file__)
        invites_directory = os.path.join(base_dir, "..",  "invites")
        db_invites = os.path.join(invites_directory, f"{server_id}_invites.sqlite")

        if not os.path.exists(db_invites):
            await interaction.send("Leaderboard database not found.", ephemeral=True)
            return

        conn_invites = sqlite3.connect(db_invites)
        cursor = conn_invites.cursor()

        # Exportiere invite_stats
        cursor.execute("SELECT inviter_id, invite_count, leave_count FROM invite_stats")
        invite_stats = cursor.fetchall()

        # Exportiere invited_users
        cursor.execute("SELECT inviter_id, user_ids, leave_ids FROM invited_users")
        invited_users = cursor.fetchall()

        # Erstelle den Inhalt der Datei im Speicher
        txt_content = "invite_stats\n"
        for inviter_id, invite_count, leave_count in invite_stats:
            txt_content += f"{inviter_id},{invite_count},{leave_count}\n"

        txt_content += "invited_users\n"
        for inviter_id, user_ids, leave_ids in invited_users:
            txt_content += f"{inviter_id},{user_ids},{leave_ids}\n"

        conn_invites.close()
        
        # Erstelle eine Datei im Speicher und sende sie
        with io.BytesIO(txt_content.encode()) as file:
            file.name = f"{server_id}_invites.txt"
            await interaction.send(file=nextcord.File(file, file.name))

    @nextcord.slash_command(name="invites", description="Display the invites and leaves of a single user")
    async def userinvites(self, interaction: Interaction, user: nextcord.Member):
        server_id = interaction.guild.id
        conn = get_invite_db_connection(server_id)  # Diese Funktion stellt die DB-Verbindung her
        cursor = conn.cursor()

        # Hole die Einladungs- und Abgangsdaten des Users
        cursor.execute('SELECT invite_count, leave_count FROM invite_stats WHERE inviter_id = ?', (user.id,))
        data = cursor.fetchone()

        if data:
            invite_count = data[0]
            leave_count = data[1]
            remaining_invites = invite_count - leave_count

            # Erstelle den Embed
            embed = nextcord.Embed(
                title=f"{interaction.user} Invites",
                description=f"<@{user.id}> has {remaining_invites} invites",
                color=0x7d89ff
            )
            embed.set_thumbnail(url=user.display_avatar.with_size(64))
            embed.set_author(name="Pyron", icon_url="https://cdn.discordapp.com/avatars/1088751762401398865/e795171c56cce3e8199e228136e77eb9.webp?size=1024&format=webp&width=0&height=256")
            embed.add_field(name="", value=f"> **{invite_count}** Total invites | **{leave_count}** left", inline=True)    
        else:
            # Falls keine Daten für den Benutzer gefunden werden
            embed = nextcord.Embed(
                title=f"Keine Daten für {user.name}",
                description=f"<@{user.id}> hat keine Einladungen oder Abgänge registriert.",
                color=0xFF0000
            )

        await interaction.response.send_message(embed=embed)

        # Datenbankverbindung schließen
        conn.close()

    @leaderboard.subcommand(description="Display the top 10 Inviters")
    async def invites(self, ctx):
        guild = ctx.guild
        server_id = guild.id

        base_dir = os.path.dirname(__file__)
        invites_directory = os.path.join(base_dir, "..",  "invites")
        db_invites = os.path.join(invites_directory, f"{server_id}_invites.sqlite")

        if not os.path.exists(db_invites):
            await ctx.send("Einladungs-Datenbank nicht gefunden.")
            return

        conn_invites = sqlite3.connect(db_invites)
        cursor = conn_invites.cursor()
        cursor.execute("""
            SELECT inviter_id, invite_count, leave_count
            FROM invite_stats
            ORDER BY (invite_count - leave_count) DESC
            LIMIT 10
        """)
        leaderboard = cursor.fetchall()

        view = InviteLeaderboardView(guild=guild)
        embed = nextcord.Embed(title="**Invite Leaderboard**", color=0x7d89ff)
        embed.set_thumbnail(url=guild.icon.with_size(64))
        embed.set_footer(text="Pyron", icon_url="https://cdn.discordapp.com/avatars/1088751762401398865/e795171c56cce3e8199e228136e77eb9.webp?size=1024&format=webp&width=0&height=256")
        
        description = ""
        for i, (inviter_id, total_invite_count, leave_count) in enumerate(leaderboard, start=1):
            net_invites = total_invite_count - leave_count
            description += f"> **{i}.** <@{inviter_id}> <:Arrow:1287446954586017812> **{net_invites}** Invites [ {total_invite_count} Total | {leave_count} Left ]\n"

        embed.description = description

        # Sende die Embed-Nachricht und speichere die Nachricht in der View
        message = await ctx.send(embed=embed, view=view)
        view.message = message  # Speichere die Nachricht für spätere Änderungen
        view.reset_timer()  # Timer starten

        conn_invites.close()


def setup(bot): 
    bot.add_cog(Leaderboard(bot))