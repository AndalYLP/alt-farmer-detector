from discord import app_commands
from discord.ext import commands
from pymongo import MongoClient
import requests
import discord
import os

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

    addSubGroup = app_commands.Group(name="add", description="add commands", parent=mainGroup)

    # ------------------------------ Resume command ------------------------------ #

    @mainGroup.command(name="resume",description="Resume the reports.")
    async def startLoop(self, interaction: discord.Interaction):
        print(interaction.user.name + " Used resume command")
        if self.bot.MuteAll:
            self.bot.MuteAll = False
            await interaction.response.send_message("Reports resumed.", delete_after=3)
        else:
            await interaction.response.send_message("The reports are already running.", delete_after=3, ephemeral=True)

    # ------------------------------- Stop command ------------------------------- #

    @mainGroup.command(name="stop",description="Stop all notifications.")
    async def stopLoop(self, interaction: discord.Interaction):
        print(interaction.user.name + " Used stop command")
        if self.bot.MuteAll == False:
            self.bot.MuteAll = True
            await interaction.response.send_message("Reports stopped.", delete_after=3)
        else:
            await interaction.response.send_message("The reports are already stopped.", delete_after=3)

    # ------------------------------- Mute command ------------------------------- #

    @mainGroup.command(name="mute",description="Mute a notification type.")
    @app_commands.describe(muteonline="Dont show online notifications", muteoffline="Dont show offline notifications",othergame="Dont show other game notifications")
    async def Mute(self, interaction: discord.Interaction, muteonline:bool, muteoffline:bool,othergame:bool):
        print(interaction.user.name + " Used mute command")
        self.bot.OnlineMuted = muteonline
        self.bot.OfflineMuted = muteoffline
        self.bot.OtherGame = othergame

        await interaction.response.send_message("changes added.", delete_after=3)

    # --------------------------- Toggle notifications --------------------------- #

    @mainGroup.command(name="notifications", description="enable/disable notifications.")
    async def notifications(interaction: discord.Interaction):
        member = interaction.guild.get_member(interaction.user.id)
        role = discord.utils.get(interaction.guild.roles, name="ping")
        MemberRole = discord.utils.get(member.roles, name="ping")
        if MemberRole:
            await member.remove_roles(role)
            await interaction.response.send_message("Notification role removed.", delete_after=5)
        else:
            await member.add_roles(role)
            await interaction.response.send_message("Notification role added.", delete_after=5)

    # ---------------------------- Add player command ---------------------------- #

    @addSubGroup.command(name="player",description="Add a player to the loop.")
    @app_commands.describe(username="the username to add.", groupname="Group name NN, None = no group.", altaccount="True if its an alt account.")
    async def addPlayer(interaction: discord.Interaction, username:str, altaccount:bool, groupname:str):
        print(interaction.user.name + " Used addplayer command")
        if not UsersCollection.find_one({"Username": username}):
            response = requests.post("https://users.roblox.com/v1/usernames/users",json={"usernames": [username],"excludeBannedUsers": True})
            if response.status_code == 200:
                responseJSON = response.json()
        
                data = responseJSON.get("data", [])
                if data and "requestedUsername" in data[0]:
                    if not UsersCollection.find_one({"UserID": data[0].get("id")}):
                        result = UsersCollection.insert_one({"UserID": data[0].get("id"), "Username": data[0].get("name"), "isAlt": True if altaccount else False, "GroupName": groupname })
                        if result.inserted_id:
                            await interaction.response.send_message("Username added to the loop.", delete_after=3)
                    else:
                        UsersCollection.update_one({"UserID": data[0].get("id")}, {"$set": {"Username": data[0].get("name"),"isAlt": True if altaccount else False,"GroupName": groupname}})
                        await interaction.response.send_message("That username is already on the list, updated his data.", delete_after=3, ephemeral=True)
                else:
                    await interaction.response.send_message("Username doesn't exist.", delete_after=3, ephemeral=True)
            else:
                await interaction.response.send_message("Error trying to verify username.", delete_after=3, ephemeral=True)
        else:
            await interaction.response.send_message("That username is already on the list.", delete_after=3, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ReportsCommands(bot))