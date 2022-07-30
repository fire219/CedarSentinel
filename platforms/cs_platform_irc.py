import irc.bot


class CedarSentinelIRC(irc.bot.SingleServerIRCBot):
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, connection, event):
        print("Connected!")

        for target in config["channels"]:
            connection.join(target)
        if config["notificationChannel"].startswith("#"):
            connection.join(config["notificationChannel"])

    def on_join(self, connection, event):
        print(f"Joined {event.target}!")

    def on_pubmsg(self, connection, event):
        # TODO: OCR functionality for image links on IRC
        author = event.source.split("!")[0].strip()
        content = event.arguments[0]
        (
            flag,
            moderate,
            author,
            content,
            inputs,
            actions,
            chat_message,
        ) = handle_message(author, content, event.target)
        if flag:
            notification_channel = config["notificationChannel"]
            if notification_channel == "*":
                notification_channel = event.target

            for submsg in chat_message.split("\n"):
                connection.privmsg(notification_channel, submsg)


def run():
    bot = CedarSentinelIRC(
        [irc.bot.ServerSpec(config["ircServer"], int(config["ircPort"]))],
        config["ircNick"],
        config["ircNick"],
    )
    bot.start()
