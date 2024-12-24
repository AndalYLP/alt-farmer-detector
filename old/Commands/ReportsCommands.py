import os

from discord import app_commands
from discord.ext import commands
from pymongo import MongoClient
from loguru import logger
import discord

from utils import error_embed, UserNotFound
import RobloxPy

# --------------------------- Environment variables -------------------------- #

MONGOURI = os.environ.get("MONGO_URI")

# ----------------------------- DataBase ----------------------------- #

Client = MongoClient(MONGOURI)
dataBase = Client["AltFarmerDetector"]
UsersCollection = dataBase["Users"]

# ------------------------------------ Cog ----------------------------------- #


class ReportsCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    mainGroup = app_commands.Group(name="reports", description="Reports commands")

    addSubGroup = app_commands.Group(
        name="add", description="add commands", parent=mainGroup
    )

    # ------------------------------ Resume command ------------------------------ #

    @mainGroup.command(name="resume", description="Resume the reports.")
    async def startLoop(self, interaction: discord.Interaction):
        print(interaction.user.name + " Used resume command")
        if self.bot.MuteAll:
            self.bot.MuteAll = False
            await interaction.response.send_message("Reports resumed.", delete_after=3)
        else:
            await interaction.response.send_message(
                "The reports are already running.", delete_after=3, ephemeral=True
            )

    # ------------------------------- Stop command ------------------------------- #

    @mainGroup.command(name="stop", description="Stop all notifications.")
    async def stopLoop(self, interaction: discord.Interaction):
        print(interaction.user.name + " Used stop command")
        if self.bot.MuteAll == False:
            self.bot.MuteAll = True
            await interaction.response.send_message("Reports stopped.", delete_after=3)
        else:
            await interaction.response.send_message(
                "The reports are already stopped.", delete_after=3
            )

    # ------------------------------- Mute command ------------------------------- #

    @mainGroup.command(name="mute", description="Mute a notification type.")
    @app_commands.describe(
        muteonline="Dont show online notifications",
        muteoffline="Dont show offline notifications",
        othergame="Dont show other game notifications",
    )
    async def Mute(
        self,
        interaction: discord.Interaction,
        muteonline: bool,
        muteoffline: bool,
        othergame: bool,
    ):
        print(interaction.user.name + " Used mute command")
        self.bot.OnlineMuted = muteonline
        self.bot.OfflineMuted = muteoffline
        self.bot.OtherGame = othergame

        await interaction.response.send_message("changes added.", delete_after=3)

    # --------------------------- Toggle notifications --------------------------- #

    @mainGroup.command(
        name="notifications", description="enable/disable notifications."
    )
    async def notifications(self, interaction: discord.Interaction):
        member = interaction.guild.get_member(interaction.user.id)
        role = discord.utils.get(interaction.guild.roles, name="ping")
        MemberRole = discord.utils.get(member.roles, name="ping")
        if MemberRole:
            await member.remove_roles(role)
            await interaction.response.send_message(
                "Notification role removed.", delete_after=5
            )
        else:
            await member.add_roles(role)
            await interaction.response.send_message(
                "Notification role added.", delete_after=5
            )

    # ---------------------------- Add player command ---------------------------- #

    @addSubGroup.command(name="player", description="Add a player to the loop.")
    @app_commands.describe(
        username="the username to add.",
        groupname="Group name, None = no group.",
        altaccount="True if its an alt account.",
    )
    async def addPlayer(
        self,
        interaction: discord.Interaction,
        username: str,
        altaccount: bool,
        groupname: str,
    ):
        logger.log(
            "COMMAND",
            f"{interaction.user.name} used {interaction.command.name} command",
        )

        try:
            user = RobloxPy.Users.get_users_by_username(username)
            user = user.get_by_requested_username(username)

            if not user:
                raise UserNotFound(username)

            if not UsersCollection.find_one({"UserID": user.userId}):
                result = UsersCollection.insert_one(
                    {
                        "UserID": user.userId,
                        "Username": user.username,
                        "isAlt": altaccount,
                        "GroupName": groupname,
                    }
                )
                if result.inserted_id:
                    await interaction.response.send_message(
                        "Username added to the loop.", delete_after=3
                    )
            else:
                UsersCollection.update_one(
                    {"UserID": user.userId},
                    {
                        "$set": {
                            "Username": user.username,
                            "isAlt": altaccount,
                            "GroupName": groupname,
                        }
                    },
                )
                await interaction.response.send_message(
                    "That username is already on the list, updated his data.",
                    delete_after=3,
                    ephemeral=True,
                )

        except Exception as e:
            logger.exception(e)
            await interaction.response.send_message(embed=error_embed(e))


async def setup(bot: commands.Bot):
    await bot.add_cog(ReportsCommands(bot))
