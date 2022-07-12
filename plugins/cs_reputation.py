from cedarscript.decorators import input, action, init
import json

known_users = {}


@init
def initialize():
    global known_users

    if config["persistKnownUsers"]:
        try:
            with open(config["persistFile"]) as f:
                known_users = json.load(f)
            print("Known users file loaded!")
        except:
            print("No known users file found. Starting fresh.")


def _get_reputation(username):
    try:
        return known_users[username]
    except KeyError:
        known_users[username] = 0
        if config["persistKnownUsers"]:
            with open(config["persistFile"], "w") as f:
                json.dump(known_users, f)
        return 0


def _set_reputation(username, value):
    known_users[username] = value

    if config["persistKnownUsers"]:
        with open(config["persistFile"], "w") as f:
            json.dump(known_users, f)


def _change_reputation(username, change):
    _set_reputation(username, _get_reputation(username) + change)


@input
def value(username):
    return _get_reputation(username)


@action
def increase(username):
    _change_reputation(username, 1)


@action
def decrease(username):
    _change_reputation(username, -1)
