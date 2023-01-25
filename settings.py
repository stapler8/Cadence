import json

DEFAULT_SETTINGS = {}
server = {}

# load our default settings and server values
if not DEFAULT_SETTINGS:
    with open("cfg/default_cfg.json") as f:
        DEFAULT_SETTINGS = json.load(f)

if not server:
    with open("cfg/server.json") as f:
        server = json.load(f)


# check if we have a settings file, and create one if needed
try:
    with open("cfg/cfg.json", "x") as f:
        json.dump(DEFAULT_SETTINGS, f)
        print("No settings file found, creating one")

except FileExistsError:
    print("Settings file found, loading...")

finally:
    with open("cfg/cfg.json") as f:
        settings = json.load(f)
    print("Settings loaded successfully")

# If file length mismatch, add missing settings to cfg.json
if len(DEFAULT_SETTINGS) != len(settings):

    print("Setting mismatch detected, adding new entries")

    # add missing entries to settings
    settings = DEFAULT_SETTINGS | settings

    # write to file
    with open("cfg/cfg.json", "w") as f:
        json.dump(settings, f)

    print("Wrote new settings to file")
