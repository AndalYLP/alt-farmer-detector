<h3 align="center">
    <br />
    Alt-farm detector
</h3>

<div align="center">

[![In-game bans](https://img.shields.io/badge/bans-400+-red?style=for-the-badge&logo=roblox&logoColor=d9e0ee)](https://www.roblox.com/games/6872265039)
![Tracked players](https://img.shields.io/badge/tracked%20players-375+-green?style=for-the-badge)
![Python version](https://img.shields.io/badge/py%20version-3.12.6-blue?style=for-the-badge&logo=python&logoColor=d9e0ee)

</div>

&nbsp;

> [!IMPORTANT]
> This bot was made with the only purpose of banning cheaters in [Roblox BedWars](https://www.roblox.com/games/6872265039/Enchants-BedWars).
>
> Please do **NOT** use this bot to stalk people.

---


## What is alt-farm?

Alt-farm is when a group of players queue with their alts to get
RP faster and with no effort, this is not allowed in Roblox BedWars

## Commands

- ### Friends
    - added `[target, usernames]`
    - ingame `[username, sameserver]`

- ### List
    - get 
    - group `[group_name]`

- ### Reports
    - add
        - player `[username, alt_account, group_name]`
    - mute `[mute_online, mute_offline, other_game]`
    - notifications
    - resume
    - stop

- ### Snipe
    - joinsoff
        - player `[username, force_update]`

    - player `[usernames]`

- ### Track
    - player `[username]`
    - stop `[username]`

## Channels

This bot follows the next channels structure:

- REPORTS
    - users-status
        > Notifies you when any account is online
    - ingame-alts
        > Notifies you when an alt is online
    - gameids
        > Sends all the gameIds the players are in
    - gameids-with-alts
        > Sends all the gameIds where at least 1 alt is in

- TRACKING
    > In this category you will find all the tracking channels you made using `/track player`

> [!NOTE]
> The bot will only send a notification if the player is playing
> [Roblox BedWars](https://www.roblox.com/games/6872265039/Enchants-BedWars).
> You can change the default game in the [constants file](src/config/constants.py) or
> if you want it to send for every game you can use
> `/reports mute other_game:False` 


## How to start
you will need the next env variables:
- **MONGO_URI**
- **COOKIE** (roblox cookie)
- **TOKEN** (discord token)

### MongoDB

For your database you need to use this structure:
- AltFarmerDetector
    - Users

### Channel Ids

You can change the channel Ids in the [constants file](src/config/constants.py).

### Host

You can host the bot for free using [Render](https://render.com/register), i recommend you to watch a tutorial on how to host a discord bot with render.

> [!NOTE]
> The bot works properly with >300 players and a free Render service,
> if you exceed this "limit" your service can get suspended due to
> a high volume of [service-initiated traffic](https://render.com/docs/free#service-initiated-traffic-threshold).

## Resources

list of resources used in this project.

### Packages

- [PyMongo](https://pypi.org/project/pymongo/)
- [Discord.py](https://pypi.org/project/discord.py/)
- [Aiohttp](https://pypi.org/project/aiohttp/)
- [Requests](https://pypi.org/project/requests/)
- [Loguru](https://pypi.org/project/loguru/)

### Host packages
These packages are only used to get a 24/7 server.

- [Waitress](https://pypi.org/project/waitress/)
- [Flask](https://pypi.org/project/Flask/)


---


<p align="center">
Released under the <a href="LICENSE.md">MIT License</a>.
</p>

<div align="center">

[![MIT License](https://img.shields.io/badge/license-MIT-white?style=for-the-badge)](LICENSE.md)

</div>