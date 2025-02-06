import discord
from discord import app_commands
from loguru import logger

from config.command_description import ReportsDesc


@app_commands.command(name="mute", description=ReportsDesc.mute)
@app_commands.describe(
    mute_online=ReportsDesc.mute_type("online"),
    mute_offline=ReportsDesc.mute_type("offline"),
    other_game=ReportsDesc.mute_type("other game"),
)
async def mute(
    interaction: discord.Interaction,
    mute_online: bool,
    mute_offline: bool,
    other_game: bool,
):
    bot = interaction.client

    logger.log(
        "COMMAND",
        f"{interaction.user.name} used {interaction.command.name} command",
    )

    bot.OnlineMuted = mute_online
    bot.OfflineMuted = mute_offline
    bot.OtherGame = other_game

    await interaction.response.send_message("changes added.", delete_after=3)
