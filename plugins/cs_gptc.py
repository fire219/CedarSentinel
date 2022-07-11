from cedarscript.command_types import Input, Action, CommandList
import gptc
import json

def initialize(_config):
    global config, classifier
    config = _config

    with open(config["spamModel"]) as f:
        spam_model = json.load(f)
    classifier = gptc.Classifier(spam_model)

def confidence(message):
    return classifier.confidence(message).get("spam", 0)

commands = CommandList([Input("confidence", confidence)])
