from discord.ui import Button, View
from discord import app_commands
from discord.ext import commands
from pymongo import MongoClient
import discord
import os

# --------------------------- Environment variables -------------------------- #

MONGOURI = os.environ.get("MONGO_URI")

# ----------------------------- DataBase ----------------------------- #

Client = MongoClient(MONGOURI)
dataBase = Client["AltFarmerDetector"]
UsersCollection = dataBase["Users"]

# ------------------------------------ Cog ----------------------------------- #


class ListCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    mainGroup = app_commands.Group(name="list", description="list commands")

    # ------------------------------- List command ------------------------------- #

    @mainGroup.command(name="get", description="List of users being tracked.")
    async def List(self, interaction: discord.Interaction):
        print(interaction.user.name + " Used list command")
        Docs = list(UsersCollection.find({}))
        page = 0
        pages = [Docs[i : i + 15] for i in range(0, len(Docs), 15)]
        print(len(pages))
        PreviousPage = Button(
            label="Previous Page", style=discord.ButtonStyle.blurple, disabled=True
        )
        NextPage = Button(label="Next Page", style=discord.ButtonStyle.blurple)

        view = View()
        view.add_item(PreviousPage)
        view.add_item(NextPage)

        async def NextPageCB(interaction):
            nonlocal page
            if page < len(pages) - 1:
                page += 1

                PreviousPage.disabled = False if not page == 0 else True
                NextPage.disabled = False if page < len(pages) - 1 else True

                embed = discord.Embed(
                    color=8585471,
                    title="User list",
                    description="".join(
                        f"**{i+1+(page*15)}.** ``{str(v["Username"])}`` **|** {str(v["UserID"])} **|** **{str(v.get("GroupName", "None"))}**\n"
                        for i, v in enumerate(pages[page])
                    ),
                )
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                NextPage.disabled = True

        async def PreviousPageCB(interaction):
            nonlocal page
            if not page == 0:
                page -= 1

                PreviousPage.disabled = False if not page == 0 else True
                NextPage.disabled = False if page < len(pages) - 1 else True

                embed = discord.Embed(
                    color=8585471,
                    title="User list",
                    description="".join(
                        f"**{i+1+(page*15)}.** ``{str(v["Username"])}`` **|** {str(v["UserID"])} **|** **{str(v.get("GroupName", "None"))}**\n"
                        for i, v in enumerate(pages[page])
                    ),
                )
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                PreviousPage.disabled = True

        NextPage.callback = NextPageCB
        PreviousPage.callback = PreviousPageCB

        embed = discord.Embed(
            color=8585471,
            title="User list",
            description="".join(
                f"**{i+1+(page*15)}.** ``{str(v["Username"])}`` **|** {str(v["UserID"])} **|** **{str(v.get("GroupName", "None"))}**\n"
                for i, v in enumerate(pages[page])
            ),
        )
        await interaction.response.send_message(embed=embed, view=view)

    # ----------------------------- Get group command ---------------------------- #

    @mainGroup.command(name="group", description="Get a list of players in a group.")
    @app_commands.describe(groupname="Name of the group to get")
    async def bygroup(self, interaction: discord.Interaction, groupname: str):
        print(interaction.user.name + " Used bygroup command")
        Docs = list(UsersCollection.find({"GroupName": groupname}))
        page = 0
        pages = [Docs[i : i + 15] for i in range(0, len(Docs), 15)]
        print(len(pages))
        PreviousPage = Button(
            label="Previous Page", style=discord.ButtonStyle.blurple, disabled=True
        )
        NextPage = Button(label="Next Page", style=discord.ButtonStyle.blurple)

        view = View()
        view.add_item(PreviousPage)
        view.add_item(NextPage)

        async def NextPageCB(interaction):
            nonlocal page
            if page < len(pages) - 1:
                page += 1

                PreviousPage.disabled = False if not page == 0 else True
                NextPage.disabled = False if page < len(pages) - 1 else True

                embed = discord.Embed(
                    color=8585471,
                    title=f"{groupname} Group list",
                    description="".join(
                        f"**{i+1+(page*15)}.** ``{str(v["Username"])}`` **|** {str(v["UserID"])} **|** **{str(v.get("GroupName", "None"))}**\n"
                        for i, v in enumerate(pages[page])
                    ),
                )
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                NextPage.disabled = True

        async def PreviousPageCB(interaction):
            nonlocal page
            if not page == 0:
                page -= 1

                PreviousPage.disabled = False if not page == 0 else True
                NextPage.disabled = False if page < len(pages) - 1 else True

                embed = discord.Embed(
                    color=8585471,
                    title=f"{groupname} Group list",
                    description="".join(
                        f"**{i+1+(page*15)}.** ``{str(v["Username"])}`` **|** {str(v["UserID"])} **|** **{str(v.get("GroupName", "None"))}**\n"
                        for i, v in enumerate(pages[page])
                    ),
                )
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                PreviousPage.disabled = True

        NextPage.callback = NextPageCB
        PreviousPage.callback = PreviousPageCB

        embed = discord.Embed(
            color=8585471,
            title=f"{groupname} Group list",
            description="".join(
                f"**{i+1+(page*15)}.** ``{str(v["Username"])}`` **|** {str(v["UserID"])} **|** **{str(v.get("GroupName", "None"))}**\n"
                for i, v in enumerate(pages[page])
            ),
        )
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(ListCommands(bot))
