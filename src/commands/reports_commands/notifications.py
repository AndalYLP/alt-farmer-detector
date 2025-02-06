import discord
from discord import app_commands
from loguru import logger


@app_commands.command(name="notifications", description="Enable/disable notifications.")
async def notifications(interaction: discord.Interaction):
    logger.log(
        "COMMAND",
        f"{interaction.user.name} used {interaction.command.name} command",
    )

    member = interaction.guild.get_member(interaction.user.id)
    role = discord.utils.get(interaction.guild.roles, name="ping")
    memberRole = discord.utils.get(member.roles, name="ping")

    if memberRole:
        await member.remove_roles(role)
        await interaction.response.send_message(
            "Notification role removed.", delete_after=5
        )
    else:
        await member.add_roles(role)
        await interaction.response.send_message(
            "Notification role added.", delete_after=5
        )
