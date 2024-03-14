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

from importlib import import_module
import yaml
from yaml.loader import SafeLoader
import pprint
import cedarscript
from cedarscript.command_types import CommandList, Command, Action, Input

version = "0.7.0"
configFile = "config.yaml"

# Extract username of message sender, and return status based on classification and/or known user bypass
def handle_message(author, content, target, flag_text=None):
    if author == config["bridgeBot"]:
        author = content.split(">", 1)[0]
        author = author.split("<", 1)[1].replace("@", "").strip()
        content = content.split(">", 1)[1]

    content = content.strip()
    author = author.strip()

    inputs = {
        input.name: input.function(message=content, username=author)
        for input in commands.inputs
    }
    actions = script(inputs)

    flag = "flag" in actions or "delete" in actions
    moderate = "delete" in actions

    for action in actions:
        if "." in action:
            commands.to_dict()[action].function(
                message=content, username=author, inputs=inputs
            )

    if flag_text is None:
        flag_text = content
    chat_message = f'{config["spamNotifyMessage"]} ( {author} -> {target} ) {flag_text}\nInputs: `{str(inputs)}`\nActions: `{str(actions)}`'
    print()
    print(
        f"{author} -> {target}: {content}\nInputs: {str(inputs)}\nActions: {str(actions)}"
    )

    return flag, moderate, author, content, inputs, actions, chat_message


def run():
    global full_config, config, commands, script
    print("Cedar Sentinel version " + version + " starting up.")
    print()

    # load files
    with open(configFile) as f:
        full_config = yaml.load(f, Loader=SafeLoader)
    config = full_config["platformConfig"][full_config["platform"]]
    print("Configuration loaded!")
    pprint.pprint(full_config)
    print()

    def do_nothing(*_, **__):
        pass

    commands = CommandList(
        [Action("flag", do_nothing), Action("delete", do_nothing)]
    )
    for name in full_config["plugins"]:
        print(f"Loading plugin `{name}`...")
        plugin = import_module(f"plugins.cs_{name}")
        plugin.config = full_config["pluginConfig"].get(name, {})
        plugin.initialize()
        plugin_contents = [getattr(plugin, i) for i in dir(plugin)]
        plugin_commands = CommandList(
            i for i in plugin_contents if isinstance(i, Command)
        )
        commands += plugin_commands.prefix(name)
        print(f"Loaded plugin `{name}`!")
        print()

    print("Inputs:", [i.name for i in commands.inputs])
    print("Actions:", [i.name for i in commands.actions])
    print()

    with open("script.txt") as f:
        script = cedarscript.load(f.read())
    print("CedarScript interpreter loaded!")
    print()

    platform = import_module(f"platforms.cs_platform_{full_config['platform']}")
    platform.config = config["private"]
    platform.handle_message = handle_message
    print(f"Loaded platform `{full_config['platform']}`!")
    print()
    platform.run()


run()
