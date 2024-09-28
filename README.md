[![Discord](https://img.shields.io/discord/1287837829711528019?label=Discord&logo=discord&style=for-the-badge)](https://discord.gg/TmZrJs3bTz)
[![Bot Invite](https://img.shields.io/badge/Invite%20Bot-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/oauth2/authorize?client_id=1088751762401398865&scope=bot&permissions=268495982)
[![GitHub stars](https://img.shields.io/badge/⭐%20Stars-2%2F5-yellow?style=for-the-badge)](https://github.com/levox00/Discord-Pyron-Bot/stargazers)
[![Top Language](https://img.shields.io/badge/Top%20Language-Python-blue?style=for-the-badge&logo=python&logoColor=white)](https://github.com/{username}/{repository})
[![💙 Contributors](https://img.shields.io/github/contributors/levox00/Discord-Pyron-Bot?style=for-the-badge&color=blue)](https://github.com/levox00/Discord-Pyron-Bot/graphs/contributors)


<div align="center">
  <img src="https://github.com/user-attachments/assets/ec8593df-1b32-4882-8885-d8064fe81449" alt="image" width="500"/>
</div>



<h1 align="center" style="display: flex; align-items: center; justify-content: center;">
  Pyron - Invite Tracking, Giveaway, Welcome messages Discord Bot
  <a href="https://discord.com/oauth2/authorize?client_id=1088751762401398865&scope=bot&permissions=268495982" style="margin-left: 10px; margin-bottom: 0px;">
    <img src="https://github.com/user-attachments/assets/605c0c96-62b8-4fcd-9f77-724914ba3608" width="150" alt="Invite Bot" />
  </a>
</h1>



<p align="center">
  <a href="https://discord.gg/TmZrJs3bTz">
    <img src="https://discordapp.com/api/guilds/1287837829711528019/widget.png?style=shield" alt="Discord Server">
  </a>
  <a href="https://github.com/levox00/Discord-InviteTracker-Bot">
    <img src="https://img.shields.io/github/stars/levox00/Discord-Pyron-Bot?style=shield&color=%23607dff" alt="GitHub Repo stars">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/GOAL-5%20Stars-green?style=shield" alt="GOAL">
  </a>
  <a>
    <img alt="GitHub top language" src="https://img.shields.io/github/languages/top/levox00/Discord-Pyron-Bot">
  </a>
  <a href="https://github.com/levox00/Discord-InviteTracker-Bot">
    <img alt="GitHub Downloads (all assets, all releases)" src="https://img.shields.io/github/downloads/levox00/Discord-Pyron-Bot/total">
  </a>
</p>

# Overview

Pyron os a powerful Discord bot designed specifically for invite tracking! Unlike many other bots that charge for premium features, Pyron offers a variety of advanced functionalities completely for free.

### Features
- Invite Tracking: Keep tabs on your server’s invites effortlessly.
- Giveaway Commands: Create and manage giveaways to engage your community and encourage participation.
- Avatar Commands: Easily retrieve and display user avatars/banners.
- Server Icon: Fetch your server's icon with a simple command.
- Server Stats: Get real-time statistics about your server, including member counts and activity levels.
- Moderation Tools: Manage your server effectively with commands for banning, kicking, and muting members.
- Flexible Hosting: If you choose to self-host, you have the freedom to customize Pyron's functionalities. You can easily enable or disable leaderboard commands, giveaways, and more according to your preferences.


<div style="display: flex; align-items: center; justify-content: center;">
  <div style="margin-right: 20px;">
    <p><strong>Why does Pyron need X permissions and how can I toggle them off?</strong></p>
    <p><a href="permissions.md">Read more here</a></p>
  </div>
  <img src="https://github.com/user-attachments/assets/6791c31d-1a62-41b0-b609-09d006b170d8" alt="Alternativtext" width="200"/>
</div>


## Command Usage

With Pyron, you can load, update, or remove commands easily when hosting the bot yourself. Use the following commands to manage your features:

- `py!load` - Load the wanted commands.
- `py!reload` - Reload the wanted commands for changes.
- `py!unload` - Unload any unnecessary commands.

  Options:
  `moderation`, `leaderboard`, `giveaway`, `commands`

<img src=https://github.com/user-attachments/assets/7babc198-a00d-4c0f-96bc-c219a9c97358 loop=infinite/>

## Self Hosting requirements

Before you start, make sure to install the necessary dependencies:

```bash
pip install -r requirements.txt
```
### Installation

1. **Install Requirements**:
   Ensure you have Python installed, then install the necessary dependencies by running:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a Discord Bot**:
   If you haven't already created a bot, follow these steps:
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications).
   - Click on "New Application".
   - Name your application and click "Create".
   - Navigate to the "Bot" tab and click "Add Bot".
   - Enable all intents
   - Add the bot to your server(s) with the required [permissions](permissions.md)

3. **Update `config.json`**:
   - Open the `config.json` file.
   - Add your bot's token (found in the "Bot" tab of the Discord Developer Portal).
   - Include your Discord User ID as the owner ID.

4. **Load Cogs**:
   Start your bot and load all necessary cogs by using the following commands in your Discord server:
   - `py!load giveaway`
   - `py!load leaderboard`
   - `py!load commands`
   - `py!load moderation`


## Upd 2.0

 - Changed database fileformat to .sqlite
 - Added Next and Previous buttons to **leaderboard invites** and **invitelist** command
 - Removed stuff that made bot response slow
 - Made all commands compatible with the new file format

<img src="https://github.com/user-attachments/assets/d23b8ddf-2302-40a8-8425-f6a93331e31d?raw=true" alt="alt text" width="200"/>


#  Commands
### Examples:

<img src="https://github.com/user-attachments/assets/5b8c5eb5-4c4e-4be3-a5c0-be1610d17f93" alt="1" width="40%"/>



<img src="https://github.com/user-attachments/assets/12e10894-8a0e-4c5a-9e52-fa6aaade73d8" alt="2" width="40%"/>

<img src="https://github.com/user-attachments/assets/7ecc9b93-a9eb-43a1-93a2-01ea4d89f423" alt="3" width="40%"/>

<img src="https://github.com/user-attachments/assets/18f33de2-1203-4ef5-ab05-29a339a75346" alt="4" width="40%"/>

<img src="https://github.com/user-attachments/assets/84c449b4-ccb5-4f5e-9ef2-3b3e417bf325" alt="4" width="40%"/>

<img src="https://github.com/user-attachments/assets/6206185c-77aa-45ec-b8b8-48bf5f4be769" alt="5" width="40%"/>

<img src="https://github.com/user-attachments/assets/f0ffa5f2-d336-49eb-a5e4-0dd3840aba48" alt="6" width="40%"/>

<img src="https://github.com/user-attachments/assets/0cee06ce-49e7-4beb-b17a-fe105dd197c5" alt="7" width="40%"/>
