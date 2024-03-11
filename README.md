![CedarSentinel](/readme_files/logo_sm.png)
## A Discord/IRC bot for automated spam detection

### About

**CedarSentinel** is a Python bot for your Discord and/or IRC servers to
automatically detect spam messages *(or any sort of message you don't like!)*.
It can alert your moderators instantly, allowing them to take action faster.
It also has support for
[Matterbridge](https://github.com/42wim/matterbridge/)-type chat bridges,
allowing it to also handle messages from many more chat platforms!

CedarSentinel can be extended using plugins. It comes with three plugins by
default. `cs_gptc` uses [GPTC](https://git.kj7rrv.com/kj7rrv/gptc) to analyze
the content of messages. `cs_reputation` tracks user reputation; this can be
incremented or decremented automatically. Finally, `cs_length` simply indicates
the number of characters in the message.

Unless you are writing your own plugin, it is unlikely that you will not want
to use the `cs_gptc` module, as it does most of the work in actually
determining whether or a message is spam. It is also a good idea to use
`cs_reputation` to prevent the bot from deleting messages from trusted users.
GPTC does occasionally flag messages incorrectly, so exempting established
users from having messages automatically deleted helps to reduce false
positives. `cs_length` may be helpful if you find that CedarSentinel often
incorrectly flags short messages as spam; GPTC seems to be less accurate at
classifying very short messages. You can configure CedarSentinel to not delete
messages under a certain length.

### How to install

```bash
git clone https://github.com/fire219/CedarSentinel.git
cd CedarSentinel
pip install pyyaml discord.py irc gptc tornado lark
cp example_config.yaml config.yaml
# edit the config file with your editor of choice!
```

After doing this, CedarSentinel can be executed in the same way as any other
Python script; the file to run is `bot.py`.

### Using CedarSentinel

In a sense, CedarSentinel is easy to set up. Once you have the config file set
how you want it, there are no commands to fiddle with in-chat. CedarSentinel
is immediately watching for spam as soon as you start it for the first time.
It comes pre-configured with a model trained on messages from the Pine64 Chat
Network.

However, it may not be trained properly for the type of spam that *you* have
to deal with. If it's not detecting your spam, or if it's detecting messages
that *aren't* spam, check out the ***How to train models*** section below.

### How to train models

As previously mentioned, CedarSentinel comes with a model trained for the
Pine64 Chat Network. If this model just isn't working for you, then it is time
to check out the GPTC module's training tool. This is accessed through a Web
interface, available at [`http://localhost:8888`](https://localhost:8888) when
CedarSentinel is running. Documentation is included on the page.

For security reasons, this tool can only be accessed from `localhost`. If you
want to use it over a network, then you can either use a reverse proxy or
access it through a command-line browser over SSH; it is designed to work well
in [Lynx](https://lynx.invisible-island.net/current/) as well as graphical
browser.

In most cases, the default model should be a good starting point, and you can
build on it instead of starting over. However, if you find that CedarSentinel
is not working well even after retraining with several days of new data, it may
be best to delete the model and start from scratch. To do this, simply stop
CedarSentinel, delete `gptc.db`, and restart the bot. This will delete the
entire model and all logged messages, allowing for a fresh start.

### CedarScript

CedarSentinel's responses to messages are defined by `script.txt`. This file is
written in CedarScript, a domain-specific language (DSL) designed for this
purpose. Please note that CedarScript is not Turing-complete; it is designed to
express simple if-else logic, not advanced algorithms.

#### Conditions

If statements have the following syntax:

```
if [condition] {
    ...
} else {
    ...
}
```

The `else` block is optional. The `[condition]` is written as a comparison
between values. The supported operators are `<`, `<=`, `==`, `!=`, `>=`, and
`>`; they work as would be expected. Multiple comparisons can be combined using
`and` and `or`; parenthesis can be used for grouping, but are not syntactically
required.

#### Inputs

Inputs are values provided to the script by CedarSentinel plugins. Their names
consist of a dollar sign (`$`), followed by the name of the plugin (without the
`cs_` prefix), a period (`.`), and the input name. These inputs are provided by
the default plugins:

| Name                 | Meaning                             |
|----------------------|-------------------------------------|
| `$gptc.confidence`   | Confidence that the message is spam |
| `$reputation.value`  | The message's author's reputation   |
| `$length.length`     | The length of the message           |

#### Actions

Actions are how the script tells CedarSentinel what to do in respone to the
message. Their names have the same format as input names, except they begin
with an at sign (`@`) instead of a dollar sign. Also, CedarSentinel itself,
without relying on plugins, provides some actions; their names do not contain
periods.

| Name                   | Meaning                                                        |
|------------------------|----------------------------------------------------------------|
| `@flag`                | Flag the message as spam                                       |
| `@delete`              | IRC: same as `flag`; Discord: flag and delete message          |
| `@gptc.log_good`       | Add the message to the model as known good                     |
| `@gptc.log_prob_good`  | Log the message for manual review as uncertain but likely good |
| `@gptc.log_unknown`    | Log the message for manual review as unknown qualiy            |
| `@gptc.log_prob_spam`  | Log the message for manual review as uncertain but likely spam |
| `@gptc.log_spam`       | Add the message to the model as known spam                     |
| `@reputation.increase` | Increase the author's reputation                               |
| `@reputation.decrease` | Decrease the author's reputation                               |

Please note that `@gptc.log_good` and `@gptc.log_spam` are best avoided.
CedarSentinel can never be entirely sure that a message is good or bad; these
actions add messages directly into the model with no human review, so there is
a significant possibility of messages being inaccurately categorized and never
detected. This, of course, will make CedarSentinel less effective. This would
most likely occur accidentally, but a malicious user could potentially
deliberately insert harmful content into the training database as well. For
these reasons, it is most likely best to instead use `@gptc.log_prob_good` and
`@gptc.log_prob_spam` instead, and review the logged messages manually using
the training tool.

### Contributors

**CedarSentinel** is primarily developed by Matthew Petry (fireTwoOneNine) and
Samuel Sloniker (kj7rrv). Feel free to fork it and push your improvements
and/or bugfixes upstream!

### License

Copyright 2021-2024 Matthew Petry (fireTwoOneNine) and Samuel Sloniker (kj7rrv)

Code from commit 9dbe028c8f8fb765e963cd5cd59b8a2b04a30178 and earlier,
including all code by Matthew Petry, was released under the MIT license, and
may still be used under its terms. Code from after that commit is released
under the GNU General Public License, version 3 or later. See `LICENSE` for
more details.
