import json

known_users = {}

def initialize(config_):
    global known_users, config
    config = config_

    if config["persistKnownUsers"]:
        try:
            with open(config["persistFile"]) as f:
                known_users = json.load(f)
            print("Known users file loaded!")
        except:
            print("No known users file found. Starting fresh.")
    print()

def change_reputation(username, change):
    try:
        known_users[username] = known_users[username] + change
    except KeyError:
        known_users[username] = change

    if config["persistKnownUsers"]:
        with open(config["persistFile"], "w") as f:
            json.dump(known_users, f)

def get_reputation(username):
    try:
        return known_users[username]
    except KeyError:
        known_users[username] = 0
        if config["persistKnownUsers"]:
            with open(config["persistFile"], "w") as f:
                json.dump(known_users, f)
        return 0
