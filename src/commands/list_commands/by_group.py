import discord
from discord import app_commands
from discord.ui import Button, View
from loguru import logger

from config.constants import USERS_COLLECTION
from config.embeds import format_list_page_embed


@app_commands.command(name="group", description="Get a list of players in a group.")
@app_commands.describe(groupname="Name of the group to get")
async def by_group(interaction: discord.Interaction, groupname: str):
    logger.log(
        "COMMAND",
        f"{interaction.user.name} used {interaction.command.name} command",
    )

    docs = list(USERS_COLLECTION.find({"GroupName": groupname}))
    page = 0
    pages = [docs[i : i + 15] for i in range(0, len(docs), 15)]

    previousPage = Button(
        label="Previous Page", style=discord.ButtonStyle.blurple, disabled=True
    )
    nextPage = Button(label="Next Page", style=discord.ButtonStyle.blurple)

    view = View()
    view.add_item(previousPage)
    view.add_item(nextPage)

    async def nextPageCB(interaction):
        nonlocal page
        if page < len(pages) - 1:
            page += 1

            previousPage.disabled = False if not page == 0 else True
            nextPage.disabled = False if page < len(pages) - 1 else True

            embed = format_list_page_embed(f"{groupname} Group", pages)
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            nextPage.disabled = True

    async def previousPageCB(interaction):
        nonlocal page
        if not page == 0:
            page -= 1

            previousPage.disabled = False if not page == 0 else True
            nextPage.disabled = False if page < len(pages) - 1 else True

            embed = format_list_page_embed(f"{groupname} Group", pages, page)
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            previousPage.disabled = True

    nextPage.callback = nextPageCB
    previousPage.callback = previousPageCB

    embed = format_list_page_embed(f"{groupname} Group", pages)
    await interaction.response.send_message(embed=embed, view=view)
