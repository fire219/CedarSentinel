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

# Copyright 2021-2022 Matthew Petry (fireTwoOneNine), Samuel Sloniker (kj7rrv)
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

from importlib import import_module
from re import M
from time import sleep
from urllib import response
import discord
import irc.bot
import gptc
import yaml
from yaml.loader import SafeLoader
import json
import datetime
import http.client
import pprint
import cedarscript
from cedarscript.command_types import CommandList, Action, Input

# import reputation_db

optionalModules = ["cv2", "pytesseract", "numpy", "requests"]
try:
    for module in optionalModules:
        import_module(module)
    ocrAvailable = True
    # following line is redundant, but is provided to suppress errors from language helpers like Pylance
    import cv2
    import pytesseract
    import numpy
    import requests

    print("All optional modules loaded. OCR features are available (if enabled in config)")
except ImportError as error:
    print("Unable to import " + module + ". OCR features are unavailable.")
    ocrAvailable = False

version = "0.6.2"
configFile = "config.yaml"

# Extract username of message sender, and return status based on classification and/or known user bypass
def handle_message(author, content, attachments=[]):
    if author == config["bridgeBot"]:
        author = content.split(">", 1)[0]
        author = author.split("<", 1)[1].replace("@", "").strip()
        content = content.split(">", 1)[1]

    # TODO: OCR functionality for image links on IRC
    if (config["ocrEnable"] == True) and (ocrAvailable == True):
        for item in attachments:
            # very naive filetype checker
            # TODO: find a better way to check image type and validity.
            filetypes = [".jpg", ".jpeg", ".png"]
            for ftype in filetypes:
                if ftype in item.url:
                    targetImage = requests.get(item.url)
                    targetArray = numpy.frombuffer(targetImage.content, numpy.uint8)
                    targetImageCV = cv2.imdecode(targetArray, cv2.IMREAD_UNCHANGED)
                    targetText = pytesseract.image_to_string(targetImageCV)
                    print("OCR result: " + targetText.strip())
                    content = content + targetText
                    break

    content = content.strip()
    author = author.strip()

    inputs = {input.name: input.function(message=content, username=author) for input in commands.inputs}
    actions = interpreter.interpret(inputs)

    flag = "flag" in actions or "delete" in actions
    moderate = "delete" in actions

    for action in actions:
        if "." in action:
            commands.to_dict()[action].function(message=content, username=author)

    return flag, moderate, author, content, inputs, actions


# Prepare and send notification about detected spam
async def sendNotifMessage(message, customMessage=""):
    notifChannel = None
    notifPing = ""

    for channel in message.guild.text_channels:
        if channel.name == config["notificationChannel"]:
            notifChannel = channel
    if notifChannel is None:
        notifChannel = message.channel
        print("Notification channel not found! Sending in same channel as potential spam.")

    for role in message.guild.roles:
        if role.name == config["spamNotifyPing"]:
            notifPing = role.mention

    if customMessage == "":
        await notifChannel.send(f'{notifPing} {"**"} {config["spamNotifyMessage"]} {"**"} {message.jump_url}')
    else:
        await notifChannel.send(customMessage)


async def messageDeleter(message):
    if config["autoDeleteAPI"] == "customMB":
        bridge = http.client.HTTPConnection(config["bridgeURL"])
        bridge.request("DELETE", "/api/message", headers={"Content-Type": "application/json"}, body='{"id": "%s", "channel": "%s", "protocol": "discord", "account": "discord.mydiscord"}' % (message.id, message.channel.name))
        response = bridge.getresponse()
        responseText = response.read()
        await sendNotifMessage(message, customMessage="**Automatic Deletion Result:** %s" % (responseText.decode("utf-8").strip()))
        await sendNotifMessage(message, customMessage="**Message was:** `%s`" % (message.content))
        alertMsg = await message.channel.send(config["publicDeleteNotice"])
        sleep(10)
        bridge.request("DELETE", "/api/message", headers={"Content-Type": "application/json"}, body='{"id": "%s", "channel": "%s", "protocol": "discord", "account": "discord.mydiscord"}' % (alertMsg.id, alertMsg.channel.name))
    if config["autoDeleteAPI"] == "discord":
        try:
            await message.delete()
        except discord.Forbidden:
            await sendNotifMessage(message, customMessage="**Automatic Deletion Result:** No permission")
            return
        except discord.NotFound:
            await sendNotifMessage(message, customMessage="**Automatic Deletion Result:** Message does not exist")
            return
        except discord.HTTPException:
            await sendNotifMessage(message, customMessage="**Automatic Deletion Result:** Failed")
            return
        await sendNotifMessage(message, customMessage="**Automatic Deletion Result:** OK")
        alertMsg = await message.channel.send(config["publicDeleteNotice"])
        sleep(10)
        await alertMsg.delete()


class BotInstance(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        if not (message.author == bot.user):
            author = message.author.name + "#" + message.author.discriminator
            content = message.content
            attachments = message.attachments
            flag, moderate, author, content, inputs, actions = handle_message(author, content, attachments)
            print(f"Message from {author} -> {message.channel}: {content}")
            print("Inputs:", inputs)
            print("Actions:", actions)

            if flag:
                await sendNotifMessage(message)
                await sendNotifMessage("Inputs: " + str(inputs))
                await sendNotifMessage("Actions: " + str(actions))

            if moderate:
                if not (config["autoDeleteAPI"] == "none"):
                    await messageDeleter(message)


class CedarSentinelIRC(irc.bot.SingleServerIRCBot):
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, connection, event):
        print("Connected!")

        for target in config["channels"].split(" "):
            connection.join(target)
        if config["notificationChannel"].startswith("#"):
            connection.join(config["notificationChannel"])

    def on_join(self, connection, event):
        print(f"Joined {event.target}!")

    def on_pubmsg(self, connection, event):
        author = event.source.split("!")[0].strip()
        content = event.arguments[0]
        flag, moderate, author, content, inputs, actions = handle_message(author, content)
        print()
        print(f"Message from {author} -> {event.target}: {content}")
        print("Inputs:", inputs)
        print("Actions:", actions)
        if flag:
            notification_channel = config["notificationChannel"]
            if notification_channel == "*":
                notification_channel = event.target

            connection.privmsg(
                notification_channel,
                f'{config["spamNotifyPing"]}: {config["spamNotifyMessage"]} ({author} -> {event.target}) {content}',
            )
            connection.privmsg(
                notification_channel,
                "Inputs: " + str(inputs),
            )
            connection.privmsg(
                notification_channel,
                "Actions: " + str(actions),
            )


print("Cedar Sentinel version " + version + " starting up.")
print()

# load files
with open(configFile) as f:
    config = yaml.load(f, Loader=SafeLoader)
print("Configuration loaded!")
pprint.pprint(config)
print()


def do_nothing(*_, **__):
    pass


plugins = {}
commands = CommandList([Action("flag", do_nothing), Action("delete", do_nothing)])
for name in config["plugins"]:
    print(f"Loading plugin `{name}`...")
    plugins[name] = import_module(f"plugins.cs_{name}")
    plugins[name].config = config["pluginConfig"].get(name, {})
    plugins[name].initialize(config=config)
    commands += plugins[name].commands.prefix(name)
    print(f"Loaded plugin `{name}`!")
    print()

with open("script.txt") as f:
    script = f.read()
interpreter = cedarscript.Interpreter(script, commands)
print("CedarScript interpreter loaded!")
print()

# Startup

if config["platform"] == "discord":
    bot = BotInstance()
    bot.run(config["discordToken"])
elif config["platform"] == "irc":
    bot = CedarSentinelIRC(
        [irc.bot.ServerSpec(config["ircServer"], int(config["ircPort"]))],
        config["ircNick"],
        config["ircNick"],
    )
    bot.start()
