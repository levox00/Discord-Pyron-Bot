import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description="Ban a member from the server")
    async def ban(self, interaction: nextcord.Interaction, member: nextcord.Member, reason: str = SlashOption(description="Reason for the ban", required=False)):
        if interaction.user.guild_permissions.ban_members:
            try:
                await member.ban(reason=reason)
                embed = nextcord.Embed(
                    title="Member Banned", 
                    description=f"{member.name} has been banned.",
                    color=nextcord.Color.green()
                )
                embed.add_field(name="Reason", value=reason if reason else "No reason provided")
                await interaction.response.send_message(embed=embed, ephemeral=False)
            except nextcord.Forbidden:
                embed = nextcord.Embed(
                    title="Bot Permission Denied", 
                    description="I do not have permission to ban members or to ban this member.",
                    color=nextcord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = nextcord.Embed(
                title="Permission Denied", 
                description="You do not have permission to ban members.",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @nextcord.slash_command(description="Kick a member from the server")
    async def kick(self, interaction: nextcord.Interaction, member: nextcord.Member, reason: str = SlashOption(description="Reason for the kick", required=False)):
        if interaction.user.guild_permissions.kick_members:
            try:
                await member.kick(reason=reason)
                embed = nextcord.Embed(
                    title="Member Kicked", 
                    description=f"{member.name} has been kicked.",
                    color=nextcord.Color.green()
                )
                embed.add_field(name="Reason", value=reason if reason else "No reason provided")
                await interaction.response.send_message(embed=embed, ephemeral=False)
            except nextcord.Forbidden:
                embed = nextcord.Embed(
                    title="Bot Permission Denied", 
                    description="I do not have permission to kick members.",
                    color=nextcord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = nextcord.Embed(
                title="Permission Denied", 
                description="You do not have permission to kick members.",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @nextcord.slash_command(description="Gives a member a timeout.")
    async def timeout(self, interaction: nextcord.Interaction, 
                      member: nextcord.Member, 
                      duration: int = SlashOption(description="Duration for timeout in minutes", required=True),
                      reason: str = SlashOption(description="Reason for timeout", required=False)):
        if interaction.user.guild_permissions.moderate_members:
            try:
                timeout_duration = datetime.timedelta(minutes=duration)
                await member.timeout(timeout_duration, reason=reason)
                embed = nextcord.Embed(
                    title="Member Timed Out",
                    description=f"<@{member.id}> got timed out for {duration} minutes.",
                    color=nextcord.Color.green()
                )
                embed.add_field(name="Reason", value=reason if reason else "No reason provided")                
                await interaction.response.send_message(embed=embed, ephemeral=False)
            except nextcord.Forbidden:
                embed = nextcord.Embed(
                    title="Bot Permission Denied", 
                    description="I do not have permission to timeout members.",
                    color=nextcord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = nextcord.Embed(
                title="Permission Denied", 
                description="You do not have permission to timeout members.",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)



def setup(bot):
    bot.add_cog(Moderation(bot))