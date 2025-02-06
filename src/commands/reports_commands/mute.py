import discord
from discord import app_commands
from loguru import logger


@app_commands.command(name="mute", description="Mute a notification type.")
@app_commands.describe(
    mute_online="Dont show online notifications.",
    mute_offline="Dont show offline notifications.",
    other_game="Dont show other game notifications.",
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
