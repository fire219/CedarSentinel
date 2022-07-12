from cedarscript.command_types import Input, Action, CommandList
import datetime
import gptc
import json


def initialize(*_, **__):
    global classifier
    with open(config["spamModel"]) as f:
        spam_model = json.load(f)
    classifier = gptc.Classifier(spam_model)


def confidence(message, *_, **__):
    return classifier.confidence(message).get("spam", 0)


def log(message, *_, **__):
    with open(config["spamFile"], "a") as f:
        log_time = str(datetime.datetime.today())
        f.write(",\n")  # append to previous JSON dump, and make this prettier for human eyes
        logEntry = {"time": log_time, "message": message, "confidence": 0}
        # TODO figure out how to get the confidence to this
        json.dump(logEntry, f)


commands = CommandList([Input("confidence", confidence), Action("log", log)])
