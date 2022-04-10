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
import cedarscript

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
                    if config["debugMode"]:
                        print("OCR result: " + targetText.strip())
                    content = content + targetText
                    break

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

    flag = "flag" in actions or "moderate" in actions
    moderate = "moderate" in actions

    return flag, moderate, confidence, author, content


# Prepare and send notification about detected spam
async def sendNotifMessage(message, confidence=0.0, customMessage=""):
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
        if config["debugMode"]:
            await notifChannel.send(f"DEBUG: Confidence value on the above message is: {confidence}")
    else:
        await notifChannel.send(customMessage)


# log message to file for later analysis
def logMessage(message, confidence):
    with open(config["spamFile"], "a") as f:
        logTime = str(datetime.datetime.today())
        f.write(",\n")  # append to previous JSON dump, and make this prettier for human eyes
        logEntry = {"time": logTime, "message": message, "confidence": confidence}
        json.dump(logEntry, f)


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
        alertMsg.delete()


class BotInstance(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        if not (message.author == bot.user):
            author = message.author.name + "#" + message.author.discriminator
            content = message.content
            attachments = message.attachments
            flag, moderate, confidence, author, content = handle_message(author, content, attachments)
            print(f"Message from {author}: {content}")
            if config["debugMode"]:
                print(confidence)
                print(f"Flagging: {flag}; Moderating: {moderate}")

            if flag:
                await sendNotifMessage(message, confidence)

            if moderate:
                if not (config["autoDeleteAPI"] == "none"):
                    await messageDeleter(message)


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
        flag, moderate, confidence, author, content = handle_message(author, content)
        print(f"Message from {author}: {content}")
        if config["debugMode"]:
            print(confidence)
            print(f"Flagging: {flag}")
        if flag:
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

with open("script.txt") as f:
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
