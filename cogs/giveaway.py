import nextcord
from nextcord import Interaction, ButtonStyle
from nextcord.ext import commands
from nextcord.ui import Button, View
import os
import json
import random
from datetime import datetime, timedelta, timezone
import asyncio
import re

intents = nextcord.Intents.default()
intents.invites = True
intents.members = True

bot = commands.Bot(command_prefix="cogs!!", intents=intents)

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

def get_giveaway_file_path(message_id):
    return os.path.join(os.path.dirname(__file__), "..",  "giveaways", f"{message_id}.json")

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='giveaway')
    async def giveaway(self, interaction: Interaction):
        pass

    @giveaway.subcommand(description="Create a giveaway")
    async def create(
        self,
        interaction: nextcord.Interaction,
        duration: str = nextcord.SlashOption(description="Duration for the giveaway in seconds", required=True),
        prize: str = nextcord.SlashOption(description="Name of the prize for the giveaway", required=True),
        winners: int = nextcord.SlashOption(description="Amount of winners for the giveaway", required=False, default=1),
        channel: nextcord.abc.GuildChannel  = nextcord.SlashOption(description="Channel where the giveaway will be hosted", required=False, default=None),
        roles: str = nextcord.SlashOption(description="Roles that can participate in the giveaway (must have 1 or more role you input)", required=False, default="@everyone"),
        extra_entries: str = nextcord.SlashOption(description="Roles that have extra entries for the giveaway", required=False, default=None),
        thumbnail: nextcord.Attachment = nextcord.SlashOption(description="Image to show on the giveaway embed", required=False, default=None),
        host: nextcord.Member = nextcord.SlashOption(description="Set the host for the giveaway", required=False, default=None)
    ):
        if interaction.guild is None:
            return
        
        if channel is None:
            channel = interaction.channel
        if not any(role.permissions.administrator for role in interaction.user.roles):
            await interaction.send("You need admin perms to use this command.", ephemeral=True)
            return


        if host == None:
            host = f"{interaction.user.id}"
        elif host != None:
            host = host.id


        # Process the roles string into a list of role IDs
        if roles.strip() == "@everyone":
            role_ids = None  # Set to None to indicate that all users can participate
        else:
            # Process the roles string into a list of role IDs
            role_ids = []
            for role in roles.split(","):
                match = re.search(r"<@&(\d+)>", role.strip())
                if match:
                    role_ids.append(int(match.group(1)))

        try:
            duration = parse_duration(duration)
        except ValueError as e:
            error_embed = nextcord.Embed(
                description=str(e),
                color=nextcord.Color.red()
            )
            error_embed.set_author(name=f"Pyron", icon_url=f"https://cdn.discordapp.com/avatars/1088751762401398865/e795171c56cce3e8199e228136e77eb9.webp?size=1024&format=webp&width=0&height=256")
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return
        # Calculate end time using timezone-aware datetime
        end_time = datetime.now(timezone.utc) + timedelta(seconds=duration)
        end_timestamp = int(end_time.timestamp())

        created_embed = nextcord.Embed(
            description=f"Successfully created giveaway in {channel.mention}",
            color=nextcord.Color.green()
        )
        await interaction.response.send_message("Giveaway created!", embed=created_embed, ephemeral=True)

        end_time = datetime.now(timezone.utc) + timedelta(seconds=duration)
        end_timestamp = int(end_time.timestamp())
        # Create the embed
        embed = nextcord.Embed(
            title=f"__{prize}__",
            description=f"**Click the <:whitetada:1284245616771203212> button below to enter!**\n> Host <:Arrow:1287446954586017812> <@{host}>\n> Winners <:Arrow:1287446954586017812> **{winners}**",
            color=0x7d89ff
        )
        embed.set_thumbnail(thumbnail)
        embed.set_author(name="Pyron", icon_url="https://cdn.discordapp.com/avatars/1088751762401398865/e795171c56cce3e8199e228136e77eb9.webp?size=1024&format=webp&width=0&height=256")
        embed.add_field(name="Ends in ", value=f"<t:{end_timestamp}:R>", inline=True)
        embed.add_field(name="Entries", value="**0** <:Members:1287442366164238407>", inline=True)
        if roles != "@everyone":
            embed.add_field(name="Required roles", value=f"{roles}", inline=False)
        else:
            pass
        if extra_entries != None:
            embed.add_field(name="Extra Entries", value=f"{extra_entries}", inline=False)
        else:
            pass
        # Add the button
        button = nextcord.ui.Button(label="Participate", emoji="<:whitetada:1284245616771203212>",style=nextcord.ButtonStyle.primary)

        async def button_callback(interaction: nextcord.Interaction):
            # Check if the user has at least one of the required roles
            if role_ids is not None:
                user_roles = [role.id for role in interaction.user.roles]
                if not any(role_id in user_roles for role_id in role_ids):
                    deny_embed = nextcord.Embed(
                        description=f"You don't have any of the required roles: {roles}, which you need to participate in this giveaway.",
                        color=nextcord.Color.red()
                    )
                    deny_embed.set_footer(text="Pyron", icon_url=f"https://cdn.discordapp.com/avatars/1088751762401398865/e795171c56cce3e8199e228136e77eb9.webp?size=1024&format=webp&width=0&height=256")
                    deny_embed.set_author(name="Entry Denied", icon_url=interaction.user.display_avatar.url)
                    await interaction.response.send_message(embed=deny_embed, ephemeral=True)
                    return

            # Path to the giveaway file
            giveaway_file_path = get_giveaway_file_path(interaction.message.id)
            
            # Ensure the file exists before modifying it
            if not os.path.exists(giveaway_file_path):
                initial_data = {"participants": [], "end_time": end_time.isoformat()}
                with open(giveaway_file_path, 'w') as file:
                    json.dump(initial_data, file, indent=4)
            
            # Update the file with the new participant
            with open(giveaway_file_path, 'r+') as file:
                data = json.load(file)
                
                # Add user to participants, and check for extra entries
                user_id = str(interaction.user.id)
                
                # Use regex to extract role IDs from the extra_entries string
                extra_roles = []
                if extra_entries:
                    role_mentions = extra_entries.split(",")
                    for role_mention in role_mentions:
                        match = re.search(r"<@&(\d+)>", role_mention.strip())
                        if match:
                            extra_roles.append(int(match.group(1)))
                
                user_roles = [role.id for role in interaction.user.roles]
                additional_entries = 1
                
                if any(role in extra_roles for role in user_roles):
                    additional_entries = 2  # User gets 2 entries if they have a role from extra_entries

                if user_id not in data["participants"]:
                    # Add user multiple times based on additional_entries
                    for _ in range(additional_entries):
                        data["participants"].append(user_id)
                    
                    file.seek(0)
                    json.dump(data, file, indent=4)
            
            current_participants = len(data["participants"])
            embed = interaction.message.embeds[0]
            embed.set_field_at(1, name="Entries", value=f"**{current_participants}** <:Members:1287442366164238407>", inline=True)
            
            # Update the message with the new embed
            await interaction.message.edit(embed=embed)
            await interaction.response.send_message("You have been added to the giveaway!", ephemeral=True)

        
        button.callback = button_callback
        view = nextcord.ui.View(timeout=None)
        view.add_item(button)

        # Send the message with embed and button
        try:
            message = await channel.send(embed=embed, view=view)
        except nextcord.HTTPException as e:
            await interaction.followup.send("Failed to send the giveaway message.", ephemeral=True)
            return
        
        # Save the giveaway file with initial data
        giveaway_id = str(message.id)
        giveaways_directory = os.path.join(os.path.dirname(__file__), "..",  "giveaways")
        os.makedirs(giveaways_directory, exist_ok=True)
        giveaway_file_path = os.path.join(giveaways_directory,  f"{giveaway_id}.json")
        
        initial_data = {"participants": [], "end_time": end_time.isoformat()}
        with open(giveaway_file_path, 'w') as f:
            json.dump(initial_data, f, indent=4)

        # Wait for the duration to elapse
        await asyncio.sleep(duration)
        
        # Load giveaway data
        if os.path.exists(giveaway_file_path):
            with open(giveaway_file_path, 'r') as file:
                data = json.load(file)
        
            # Disable the button after the giveaway ends
            giveaway_message = await channel.fetch_message(giveaway_id)
            button.disabled = True
            await giveaway_message.edit(view=view)

            if data["participants"]:
                # Ensure the number of winners does not exceed the number of participants
                num_winners = min(winners, len(data["participants"]))
                winners_ids = random.sample(data["participants"], num_winners)
                
                winner_mentions = []
                for winner_id in winners_ids:
                    winner = bot.get_user(int(winner_id))
                    if winner:
                        try:
                            winner_embed = nextcord.Embed(
                                title="Congrats <a:9142tada:1284228937240674474>",
                                description=f"You won the giveaway of **{prize}** in __{channel.guild.name}__!",
                                color=0x7d89ff
                            )
                            link_button = nextcord.ui.Button(
                                label="Jump to giveaway", 
                                url=f"https://discord.com/channels/{channel.guild.id}/{channel.id}/{message.id}", 
                                style=nextcord.ButtonStyle.link
                            )
                            # Create a view with the button
                            view = nextcord.ui.View()
                            view.add_item(link_button)

                            # Send the embed with the button
                            await winner.send(embed=winner_embed, view=view)
                        except nextcord.Forbidden:
                            # Handle the case where the bot cannot send a DM
                            pass
                    winner_mentions.append(f"<@{winner_id}>")
                
                # Notify the channel with a mention
                winner_embed = nextcord.Embed(
                    title="Congrats <a:9142tada:1284228937240674474>",
                    description=f"{', '.join(winner_mentions)} won the giveaway of [__{prize}__](https://discord.com/channels/{channel.guild.id}/{channel.id}/{message.id})!",
                    color=0x7d89ff
                )
                embed.set_author(name="Pyron", icon_url="https://cdn.discordapp.com/avatars/1088751762401398865/e795171c56cce3e8199e228136e77eb9.webp?size=1024&format=webp&width=0&height=256")
                winner_embed.add_field(name=f"", value=f"-# </giveaway reroll:1284199582787436605> + `{message.id}` to reroll", inline=True)
                await giveaway_message.reply(f"Congratulations {', '.join(winner_mentions)}, you won the {prize} giveaway!", embed=winner_embed)
            else:
                noentry_embed = nextcord.Embed(
                    description=f"No participants for [__{prize}__](https://discord.com/channels/{channel.guild.id}/{channel.id}/{message.id})!",
                    color=nextcord.Color.red()
                )
                noentry_embed.set_author(name="Pyron", icon_url="https://cdn.discordapp.com/avatars/1088751762401398865/e795171c56cce3e8199e228136e77eb9.webp?size=1024&format=webp&width=0&height=256")
                noentry_embed.set_footer(text="No reroll possible!")
                os.remove(giveaway_file_path)
                # Notify the channel if there were no participants
                await giveaway_message.reply(embed=noentry_embed)

            # Delete the giveaway file
            # os.remove(giveaway_file_path)
        else:
            await channel.send(f"Failed to find the giveaway file for giveaway ID {giveaway_id}.")

    @giveaway.subcommand(description="Reroll a giveaway")
    async def reroll(
        self,
        interaction: nextcord.Interaction,
        giveaway_id: str = nextcord.SlashOption(description="The giveaway message ID", required=True),
        winners: int = nextcord.SlashOption(description="Number of winners to reroll", required=True),
    ):
        giveaways_directory = os.path.join(os.path.dirname(__file__), "..",  "giveaways")
        giveaway_file_path = os.path.join(giveaways_directory,  f"{giveaway_id}.json")
        if not any(role.permissions.administrator for role in interaction.user.roles):
            await interaction.send("You need admin perms to use this command.", ephemeral=True)
            return
        
        # Check if the giveaway file exists
        if not os.path.exists(giveaway_file_path):
            await interaction.response.send_message(f"Giveaway with ID {giveaway_id} not found.", ephemeral=True)
            return

        # Load giveaway data from the file
        with open(giveaway_file_path, "r") as file:
            data = json.load(file)

        # Ensure there are participants in the giveaway
        if not data["participants"]:
            await interaction.response.send_message("No participants found for this giveaway.", ephemeral=True)
            return

        # Ensure the number of winners does not exceed the number of participants
        num_winners = min(winners, len(data["participants"]))
        
        # Select unique winners
        winners_ids = random.sample(data["participants"], num_winners)

        winner_mentions = [f"<@{winner_id}>" for winner_id in winners_ids]
        
        # Retrieve the original giveaway message to extract the prize from the embed
        giveaway_message = await interaction.channel.fetch_message(int(giveaway_id))
        if giveaway_message and giveaway_message.embeds:
            prize = giveaway_message.embeds[0].title  # Prize is stored in the title of the embed
        else:
            prize = "Unknown Prize"
        winner_embed = nextcord.Embed(
            title="Congrats <a:9142tada:1284228937240674474>",
            description=f"{', '.join(winner_mentions)} won the giveaway of [__{prize}__](https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{giveaway_id})!",
            color=0x7d89ff
        )
        # Announce the rerolled winners
        winner_embed.set_author(name="Giveaway Rerolled", icon_url="https://cdn.discordapp.com/attachments/1281654597248880753/1284284722163486802/Unbenanntes_Projekt.gif?ex=66e612da&is=66e4c15a&hm=29e7a5ad9439b1c805fd4834cd2dc35d0d59d81c220d4f29845d8c608eb6c69f&")
        await interaction.channel.send(f"Congratulations {', '.join(winner_mentions)}, you won the {prize} giveaway!", embed=winner_embed)
        completed_embed = nextcord.Embed(
            description="Successfully Rerolled",
        )
        await interaction.response.send_message(f"Reroll completed with {num_winners} winner(s)!", ephemeral=True)

def setup(bot):
    bot.add_cog(Giveaway(bot))