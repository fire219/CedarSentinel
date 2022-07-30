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
import yaml
from yaml.loader import SafeLoader
import pprint
import cedarscript
from cedarscript.command_types import CommandList, Command, Action, Input

version = "0.7.0"
configFile = "config.yaml"

# Extract username of message sender, and return status based on classification and/or known user bypass
def handle_message(author, content, target, attachments=[], flag_text=None):
    if author == config["bridgeBot"]:
        author = content.split(">", 1)[0]
        author = author.split("<", 1)[1].replace("@", "").strip()
        content = content.split(">", 1)[1]

    if (config["ocrEnable"] == True) and (ocrAvailable == True):
        for item in attachments:
            # very naive filetype checker
            # TODO: find a better way to check image type and validity.
            filetypes = [".jpg", ".jpeg", ".png"]
            for ftype in filetypes:
                if ftype in item.url:
                    targetImage = requests.get(item.url)
                    targetArray = numpy.frombuffer(
                        targetImage.content, numpy.uint8
                    )
                    targetImageCV = cv2.imdecode(
                        targetArray, cv2.IMREAD_UNCHANGED
                    )
                    targetText = pytesseract.image_to_string(targetImageCV)
                    print("OCR result: " + targetText.strip())
                    content = content + targetText
                    break

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

    if config["ocrEnable"]:
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

            print(
                "All optional modules loaded. OCR features are available (if enabled in config)"
            )
        except ImportError as error:
            print(
                "Unable to import " + module + ". OCR features are unavailable."
            )
            ocrAvailable = False
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
