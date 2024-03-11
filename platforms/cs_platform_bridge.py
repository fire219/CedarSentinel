import discord
from time import sleep
import http.client
import threading
import asyncio
import pyrcb2


# Prepare and send notification about detected spam
async def send_notif_message(original_message, message):
    notifChannel = None
    notifPing = ""

    for channel in original_message.guild.text_channels:
        if channel.name == config["notificationChannel"]:
            notifChannel = channel
    if notifChannel is None:
        notifChannel = original_message.channel
        print(
            "Notification channel not found! Sending in same channel as potential spam."
        )

    await notifChannel.send(message)


async def delete_message_discord(message):
    try:
        await message.delete()
    except discord.Forbidden:
        await send_notif_message(
            message, "**Automatic Deletion Result:** No permission"
        )
        return
    except discord.NotFound:
        await send_notif_message(
            message, "**Automatic Deletion Result:** Message does not exist"
        )
        return
    except discord.HTTPException:
        await send_notif_message(
            message, "**Automatic Deletion Result:** Failed"
        )
        return
    await send_notif_message(message, "**Automatic Deletion Result:** OK")
    await send_notif_message(
        message, "**Message was:** `%s`" % (message.content)
    )
    alertMsg = await message.channel.send(config["publicDeleteNotice"])
    sleep(10)
    await alertMsg.delete()


class DiscordBotInstance(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        if not (message.author == self.user):
            author = (
                "[D]" + message.author.name + "#" + message.author.discriminator
            )
            content = message.content
            (
                flag,
                moderate,
                author,
                content,
                inputs,
                actions,
                chat_message,
            ) = handle_message(
                author, content, message.channel, message.jump_url
            )

            if flag:
                await send_notif_message(message, chat_message)

            if moderate:
                await delete_message_discord(message)
            else:
                await irc_bot.bridge(
                    "D", message.channel.name, message.author.name, content
                )

    async def _bridge(self, platform, channel, author, message):
        for discord_channel in self.guilds[0].text_channels:
            if discord_channel.name == equivalents[platform][channel]["D"]:
                break
        await discord_channel.send(f"[{platform}] <{author}> {message}")

    async def bridge(self, platform, channel, author, message):
        asyncio.run_coroutine_threadsafe(self._bridge(platform, channel, author, message), self.loop)


class CedarSentinelIRC:
    def __init__(self, server, port, nick, loop):
        self.server = server
        self.port = port
        self.nick = nick
        self.loop = loop

        self.bot = pyrcb2.IRCBot(log_communication=True)
        self.bot.load_events(self)

    async def run(self):
        async def init():
            await self.bot.connect(self.server, self.port)
            await self.bot.register(self.nick)
            
            print("Connected!")

            for target in config["channels"]:
                self.bot.join(target)

        await self.bot.run(init())

    @pyrcb2.Event.join
    def on_join(self, sender, channel):
        if sender == self.bot.nickname:
            print(f"Joined {channel}!")

    @pyrcb2.Event.privmsg
    async def on_privmsg(self, author, channel, content):
        if not channel:
            pass

        (
            flag,
            moderate,
            author,
            content,
            inputs,
            actions,
            chat_message,
        ) = handle_message(author, content, channel)
        if flag:
            #TODO do something with flags
            #notification_channel = config["notificationChannel"]
            #if notification_channel == "*":
            #    notification_channel = event.target
#
 #           for submsg in chat_message.split("\n"):
  #              connection.privmsg(notification_channel, submsg)
            pass

        if not moderate:
            await discord_bot.bridge("I", channel, author, content)

    async def _bridge(self, platform, channel, author, message):
        target=equivalents[platform][channel]["I"]
        for line in message.replace("\r", "").split("\n"):
            self.bot.privmsg(
                target,
                f"[{platform}] <{author}> {line}",
            )

    async def bridge(self, platform, channel, author, message):
        asyncio.run_coroutine_threadsafe(self._bridge(platform, channel, author, message), self.loop)

async def run_irc(irc_bot):
    await irc_bot.run()

def run():
    global equivalents
    equivalents = {"I": {}, "D": {}}
    for irc_channel, discord_channel in config["chanGroups"]:
        equivalents["I"][irc_channel] = {"D": discord_channel}
        equivalents["D"][discord_channel] = {"I": irc_channel}

    global irc_bot

    irc_loop = asyncio.get_event_loop()
    irc_bot = CedarSentinelIRC(
        config["ircServer"],
        int(config["ircPort"]),
        config["ircNick"],
        irc_loop,
    )
    threading.Thread(target=irc_loop.run_until_complete, args=(run_irc(irc_bot),)).start()

    global discord_bot
    intents = discord.Intents.default()
    intents.message_content = True
    discord_bot = DiscordBotInstance(intents=intents)
    discord_bot.run(config["discordToken"])
