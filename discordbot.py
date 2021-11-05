# Cedar Sentinel
# A Discord Bot for using trained models to detect spam
# Built for the Pine64 Chat Network

# Copyright 2021 Matthew Petry (fireTwoOneNine)
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
import gptc
import yaml
from yaml.loader import SafeLoader
import json

version = "0.1"
configFile = "config.yaml"

knownUsers = {}

# Check if a user meets the threshold for classification immunity
def validateUser(username): 
    try:
        knownUsers[username] = knownUsers[username] + 1
        userAppearances = knownUsers[username]
        if (config["persistKnownUsers"]):
            with open(config["persistFile"], 'w') as f:
                json.dump(knownUsers, f)
        if (userAppearances > config["messageThreshold"]):
            print("classify bypass")
            return True
        else: 
            return False
    except KeyError:
        knownUsers[username] = 1
        if (config["persistKnownUsers"]):
            with open(config["persistFile"], 'w') as f:
                json.dump(knownUsers, f)
        return False


# Extract username of message sender, and return status based on classification and/or known user bypass
def checkMessage(message):
    # begin discord-specific section
    author = message.author.name+"#"+message.author.discriminator
    content = message.content
    # end discord-specific section

    knownUser = False
    if (config["classifyBypass"]):
        if (author == config["bridgeBot"]):
            author = content.split('>', 1)[0]
            author = author.split('<', 1)[1].replace('@', '').strip()
        knownUser = validateUser(author.name)
    if knownUser:
        return "good"
    else: 
        return classifier.classify(content)


# Prepare and send notification about detected spam    
async def sendNotifMessage(message):
    # begin discord-specific code
    notifChannel = None
    notifPing = ""
    for channel in message.guild.text_channels:
        if channel.name == config["notificationChannel"]:
            notifChannel = channel
    for role in message.guild.roles:
        if role.name == config["spamNotifyPing"]:
            notifPing = role.mention
    if notifChannel:
        await notifChannel.send(notifPing+" "+config["spamNotifyMessage"]+" "+message.jump_url)
    else:
        print("Notification channel not found! Sending in same channel as potential spam.")
        await message.channel.send(notifPing+" "+config["spamNotifyMessage"])
    # end discord-specific code

# begin discord-specific code
class BotInstance(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))
        messageClass = None
        if not (message.author == bot.user): 
            messageClass = str(checkMessage(message))
        if messageClass == "spam": 
            await sendNotifMessage(message)
# end discord-specific code

# load files 
with open(configFile) as f:
    config = yaml.load(f, Loader=SafeLoader)
with open(config["spamModel"]) as f:
    spamModel = json.load(f)
if (config["persistKnownUsers"]):
    try:
        with open(config["persistFile"]) as f:
            knownUsers = json.load(f)
    except: 
        print("No known users file found. Starting fresh.")

#Startup
print("Cedar Sentinel version "+version+" starting up.")
classifier = gptc.Classifier(spamModel)
print("Spam Model Loaded!")
bot = BotInstance()
# begin discord-specific code
bot.run(config["discordToken"])
# end discord-specific code
