import discord
from discord import app_commands
from loguru import logger


@app_commands.command(name="resume", description="Resume the reports.")
async def resume_loop(interaction: discord.Interaction):
    bot = interaction.client

    logger.log(
        "COMMAND",
        f"{interaction.user.name} used {interaction.command.name} command",
    )

    if bot.MuteAll:
        bot.MuteAll = False
        await interaction.response.send_message("Reports resumed.", delete_after=3)
    else:
        await interaction.response.send_message(
            "The reports are already running.", delete_after=3, ephemeral=True
        )
