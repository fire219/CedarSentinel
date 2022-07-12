import discord
from time import sleep
import http.client


# Prepare and send notification about detected spam
async def sendNotifMessage(original_message, message):
    notifChannel = None
    notifPing = ""

    for channel in original_message.guild.text_channels:
        if channel.name == config["notificationChannel"]:
            notifChannel = channel
    if notifChannel is None:
        notifChannel = original_message.channel
        print("Notification channel not found! Sending in same channel as potential spam.")

    await notifChannel.send(message)


async def messageDeleter(message):
    if config["autoDeleteAPI"] == "customMB":
        bridge = http.client.HTTPConnection(config["bridgeURL"])
        bridge.request("DELETE", "/api/message", headers={"Content-Type": "application/json"}, body='{"id": "%s", "channel": "%s", "protocol": "discord", "account": "discord.mydiscord"}' % (message.id, message.channel.name))
        response = bridge.getresponse()
        responseText = response.read()
        await sendNotifMessage(message, "**Automatic Deletion Result:** %s" % (responseText.decode("utf-8").strip()))
        await sendNotifMessage(message, "**Message was:** `%s`" % (message.content))
        alertMsg = await message.channel.send(config["publicDeleteNotice"])
        sleep(10)
        bridge.request("DELETE", "/api/message", headers={"Content-Type": "application/json"}, body='{"id": "%s", "channel": "%s", "protocol": "discord", "account": "discord.mydiscord"}' % (alertMsg.id, alertMsg.channel.name))
    if config["autoDeleteAPI"] == "discord":
        try:
            await message.delete()
        except discord.Forbidden:
            await sendNotifMessage(message, "**Automatic Deletion Result:** No permission")
            return
        except discord.NotFound:
            await sendNotifMessage(message, "**Automatic Deletion Result:** Message does not exist")
            return
        except discord.HTTPException:
            await sendNotifMessage(message, "**Automatic Deletion Result:** Failed")
            return
        await sendNotifMessage(message, "**Automatic Deletion Result:** OK")
        await sendNotifMessage(message, "**Message was:** `%s`" % (message.content))
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
            flag, moderate, author, content, inputs, actions, chat_message = handle_message(author, content, message.channel, attachments, message.jump_url)

            if flag:
                await sendNotifMessage(message, chat_message)

            if moderate:
                if not (config["autoDeleteAPI"] == "none"):
                    await messageDeleter(message)

def run():
    global bot
    bot = BotInstance()
    bot.run(config["discordToken"])
