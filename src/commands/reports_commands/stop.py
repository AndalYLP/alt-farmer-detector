import discord
from discord import app_commands
from loguru import logger


@app_commands.command(name="stop", description="Stop all notifications.")
async def stop_loop(interaction: discord.Interaction):
    bot = interaction.client

    logger.log(
        "COMMAND",
        f"{interaction.user.name} used {interaction.command.name} command",
    )

    if bot.MuteAll == False:
        bot.MuteAll = True
        await interaction.response.send_message("Reports stopped.", delete_after=3)
    else:
        await interaction.response.send_message(
            "The reports are already stopped.", delete_after=3, ephemeral=True
        )
