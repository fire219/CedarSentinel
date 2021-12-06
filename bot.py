#     / \
#     [o]<===========
#    /===\
#   /_____\
#   /     \
#  /_______\
#  /       \
# /_________\
#
# Cedar Sentinel
# A Discord Bot for using trained models to detect spam
# Built for the Pine64 Chat Network

# Copyright 2021 Matthew Petry (fireTwoOneNine), Samuel Sloniker (kj7rrv)
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import discord
import irc.bot
import gptc
import yaml
from yaml.loader import SafeLoader
import json
import datetime
import cedarscript

version = "0.4"
configFile = "config.yaml"

knownUsers = {}

def change_reputation(username, change):
    try:
        knownUsers[username] = knownUsers[username] + change
    except KeyError:
        knownUsers[username] = change

    if config["persistKnownUsers"]:
        with open(config["persistFile"], "w") as f:
            json.dump(knownUsers, f)

def get_reputation(username):
    try:
        return knownUsers[username]
    except KeyError:
        knownUsers[username] = 0
        if config["persistKnownUsers"]:
            with open(config["persistFile"], "w") as f:
                json.dump(knownUsers, f)
        return 0

# Extract username of message sender, and return status based on classification and/or known user bypass
def handle_message(author, content):
    if author == config["bridgeBot"]:
        author = content.split(">", 1)[0]
        author = author.split("<", 1)[1].replace("@", "").strip()
        content = content.split(">", 1)[1]

    confidences = {
        "good": 0,
        "spam": 0,
    }  # set defaults for good and spam to prevent KeyErrors in parsing
    confidences.update(classifier.confidence(content))

    content = content.strip()
    author = author.strip()

    confidence = confidences["spam"]
    length = len(content)
    reputation = get_reputation(author)

    actions = interpreter.interpret(confidence, length, reputation)

    if "log" in actions:
        logMessage(content, confidence)

    if "increasereputation" in actions:
        change_reputation(author, 1)
    elif "decreasereputation" in actions:
        change_reputation(author, -1)

    is_spam = "flag" in actions

    return is_spam, confidence, author, content


# Prepare and send notification about detected spam
async def sendNotifMessage(message, confidence):
    notifChannel = None
    notifPing = ""

    for channel in message.guild.text_channels:
        if channel.name == config["notificationChannel"]:
            notifChannel = channel
    if notifChannel is None:
        notifChannel = message.channel
        print(
            "Notification channel not found! Sending in same channel as potential spam."
        )

    for role in message.guild.roles:
        if role.name == config["spamNotifyPing"]:
            notifPing = role.mention

    await notifChannel.send(
        f'{notifPing} {config["spamNotifyMessage"]} {message.jump_url}'
    )
    if config["debugMode"]:
        await notifChannel.send(
            f"DEBUG: Confidence value on the above message is: {confidence}"
        )


# log message to file for later analysis
def logMessage(message, confidence):
    with open(config["spamFile"], "a") as f:
        logTime = str(datetime.datetime.today())
        f.write(
            ",\n"
        )  # append to previous JSON dump, and make this prettier for human eyes
        logEntry = {"time": logTime, "message": message, "confidence": confidence}
        json.dump(logEntry, f)


class BotInstance(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        if not (message.author == bot.user):
            author = message.author.name + "#" + message.author.discriminator
            content = message.content
            is_spam, confidence, author, content = handle_message(author, content)
            print(f"Message from {author}: {content}")
            if config["debugMode"]:
                print(confidence)
            if is_spam:
                await sendNotifMessage(message, confidence)


class CedarSentinelIRC(irc.bot.SingleServerIRCBot):
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, connection, event):
        for target in config["channels"].split(" "):
            connection.join(target)
        if config["notificationChannel"].startswith("#"):
            connection.join(config["notificationChannel"])
        print("Connected!")

    def on_pubmsg(self, connection, event):
        author = event.source.split("!")[0].strip()
        content = event.arguments[0]
        is_spam, confidence, author, content = handle_message(author, content)
        print(f"Message from {author}: {content}")
        if config["debugMode"]:
            print(confidence)
        if is_spam:
            notification_channel = config["notificationChannel"]
            if notification_channel == "*":
                notification_channel = event.target

            connection.privmsg(
                notification_channel,
                f'{config["spamNotifyPing"]}: {config["spamNotifyMessage"]} ({author} -> {event.target}) {content}',
            )
            if config["debugMode"]:
                connection.privmsg(
                    notification_channel,
                    f"DEBUG: Confidence value on the above message is: {confidence}",
                )


# load files
with open(configFile) as f:
    config = yaml.load(f, Loader=SafeLoader)
with open(config["spamModel"]) as f:
    spamModel = json.load(f)

if config["persistKnownUsers"]:
    try:
        with open(config["persistFile"]) as f:
            knownUsers = json.load(f)
    except:
        print("No known users file found. Starting fresh.")

# Startup
print("Cedar Sentinel version " + version + " starting up.")
classifier = gptc.Classifier(spamModel)
print("Spam Model Loaded!")

with open('script.txt') as f:
    script = f.read()
interpreter = cedarscript.Interpreter(script)
print("CedarScript Interpreter Loaded!")

if config["platform"] == "discord":
    bot = BotInstance()
    bot.run(config["discordToken"])
elif config["platform"] == "irc":
    print(config)
    bot = CedarSentinelIRC(
        [irc.bot.ServerSpec(config["ircServer"], int(config["ircPort"]))],
        config["ircNick"],
        config["ircNick"],
    )
    bot.start()
