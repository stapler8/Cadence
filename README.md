# Cadence

Setup guide:
    Download Cadence to your working directory
    Run the following: 

        python3 -m venv venv
        source venv/bin/activate
        pip3 install -r requirements.txt
        echo "TOKEN=<your bot token>" > .env

Run the bot inside your venv:
    
    source venv/bin/activate
    python3 build.py

Once in discord:    
    /setadminrole <id>, if you set the ID incorrectly you must edit cfg/cfg.json manually.
    After setting this, the bot must be restarted.

Cadence bot settings:

    adminRoleID: Set the role ID for your admin role. (Must be changed with /setadminrole command)

    botStatus: Set the bot's status message

    clubhouseRoleID: If set, restricts access to certain commands.

    colourPrefix: The prefix used for colour roles to be detected by the bot.

    colourRolesEnabled: Determines if colour roles will be used by the server

    levelsMaxLevel: The maximum level that can be attained by a user

    levelsExpCooldown: The cooldown before a user can be granted more Exp for sending messages.

    levelsPingOnLevelUp: Whether or not users should be @ mentioned on leveling up.

    levelsMinLevelToMention: The minimum level a user must have before the bot sends a levelup message.

    musicVoteSkip: Set if you want users to vote on skipping songs (Default: false)

    musicVoteSkipRatio: Set the ratio required to voteskip, 0-1. (Default: 0.5)

    musicSkipRequiresAdmin: Set if skipping songs requires admin role (Default: false)

    musicRequiresRole: Set if music commands require a specific role

    musicRole: Used by musicRequiresRole

true/false settings ARE case-sensitive

Credits:

Thank you to joek13, their MusicBot framework was an amazing base for Cadence's music functionality.
https://github.com/joek13/py-music-bot