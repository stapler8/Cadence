# Cadence

Setup guide:
    Download Cadence to your working directory
    Run `touch .env`
    Run `echo "TOKEN=<your bot token>" > .env`
    Run the bot inside your venv

Once in discord:    
    /setadminrole <id>, if you set the ID incorrectly you must edit cfg/cfg.json manually.

Cadence bot settings:

    adminRoleID: Set the role ID for your admin role. (Must be changed with /setadminrole command)

    botStatus: Set the bot's status message

    musicVoteSkip: Set if you want users to vote on skipping songs (Default: false)

    musicVoteSkipRatio: Set the ratio required to voteskip, 0-1. (Default: 0.5)

    musicSkipRequiresAdmin: Set if skipping songs requires admin role (Default: false)

    musicRequiresRole: Set if music commands require a specific role

    musicRole: Used by musicRequiresRole

true/false settings ARE case-sensitive

Credits:

Thank you to joek13, their MusicBot framework was an amazing base for Cadence's music functionality.
https://github.com/joek13/py-music-bot