<div align="center">
  <img src="https://github.com/user-attachments/assets/5a6e0f73-7c59-4ceb-8abc-04f13c1b21db" alt="image" width="900"/>
</div>



<h1 align="center" style="display: flex; align-items: center; justify-content: center;">
  Pyron - Invite Tracking, Giveaway Discord Bot
  <a href="https://discord.com/oauth2/authorize?client_id=1088751762401398865&scope=bot&permissions=268495982" style="margin-left: 10px; margin-bottom: 0px;">
    <img src="https://github.com/levox00/discord-InviteTracker-Giveaway-Bot/blob/main/images/Bt2.png" width="150" alt="Invite Bot" />
  </a>
</h1>




<p align="center">
  <a href="https://discord.gg/TmZrJs3bTz">
    <img src="https://discordapp.com/api/guilds/1287837829711528019/widget.png?style=shield" alt="Discord Server">
  </a>
  <a href="https://github.com/levox00/Discord-InviteTracker-Bot">
    <img src="https://img.shields.io/github/stars/levox00/Discord-InviteTracker-Bot?style=shield&color=%23607dff" alt="GitHub Repo stars">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/GOAL-2%20Stars-green?style=shield" alt="GOAL">
  </a>
  <a href="https://github.com/levox00/Discord-InviteTracker-Bot">
    <img src="https://img.shields.io/github/downloads/levox00/Discord-InviteTracker-Bot/total.svg?style=shield" alt="Monthly Downloads">
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
  <img src="https://github.com/user-attachments/assets/6a1e2f32-6bba-4e73-99d7-88c787cc566f" alt="Alternativtext" width="200"/>
</div>

## Command Usage

With Pyron, you can load, update, or remove commands easily when hosting the bot yourself. Use the following commands to manage your features:

- `py!load` - Load the wanted commands.
- `py!reload` - Reload the wanted commands for changes.
- `py!unload` - Unload any unnecessary commands.

  Options:
  `moderation`, `leaderboard`, `giveaway`, `commands`

<img src=https://github.com/user-attachments/assets/1d855880-d4d3-4caf-80c8-f4b18a64b908 loop=infinite/>

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

<img src="https://github.com/user-attachments/assets/7d669ccc-8bb6-4b1f-8fe1-ce858581d3bb?raw=true" alt="alt text" width="200"/>



## Commands

### Help Command
<img src="https://github.com/levox00/discord-InviteTracker-Giveaway-Bot/blob/main/images/help.png?raw=true" alt="alt text" width="400"/>

### Giveaway Create Command
<img src="https://github.com/levox00/discord-InviteTracker-Giveaway-Bot/blob/main/images/gw-create.png?raw=true" alt="alt text" width="400"/>

### Giveaway Reroll Command
<img src="https://github.com/levox00/discord-InviteTracker-Giveaway-Bot/blob/main/images/gw-reroll.png?raw=true" alt="alt text" width="400"/>

### Leaderboard Invites
<img src="https://github.com/levox00/discord-InviteTracker-Giveaway-Bot/blob/main/images/leaderboard.png?raw=true" alt="alt text" width="400"/>

### User Invites
<img src="https://github.com/levox00/discord-InviteTracker-Giveaway-Bot/blob/main/images/user-invites.png?raw=true" alt="alt text" width="400"/>

### Inviter Command
<img src="https://github.com/levox00/discord-InviteTracker-Giveaway-Bot/blob/main/images/inviter.png?raw=true" alt="alt text" width="400"/>

### Invitelists Command
<img src="https://github.com/levox00/discord-InviteTracker-Giveaway-Bot/blob/main/images/invlist.png?raw=true" alt="alt text" width="400"/>

### Leaderboard Export Command
<img src="https://github.com/levox00/discord-InviteTracker-Giveaway-Bot/blob/main/images/export.png?raw=true" alt="alt text" width="400"/>

### Leaderboard Replace/Import Command
<img src="https://github.com/levox00/discord-InviteTracker-Giveaway-Bot/blob/main/images/replace.png?raw=true" alt="alt text" width="400"/>

### Other commands
``/avatar`` Displays someones avatar (Profile/Banner) -> [EXAMPLE](https://github.com/levox00/discord-InviteTracker-Giveaway-Bot/blob/main/images/banner.png?raw=True)**

``/server icon`` display the server icon [EXAMPLE](https://github.com/levox00/discord-InviteTracker-Giveaway-Bot/blob/main/images/servericon.png?raw=True)

``/server stats`` display server stats -> [EXAMPLE](https://github.com/levox00/discord-InviteTracker-Giveaway-Bot/blob/main/images/stats.png?raw=True)
