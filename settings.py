import json

# load our default settings and server values
with open("cfg/default_cfg.json") as f:
    DEFAULT_SETTINGS = json.load(f)

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

if len(DEFAULT_SETTINGS) > len(settings):
    print("WARN: Settings file OUT OF DATE")
    print("Please delete cfg.json and re-run to update")
