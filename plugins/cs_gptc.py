import cspapi
import datetime
import gptc
import json


@cspapi.init
def initialize():
    global classifier
    with open(config["spamModel"]) as f:
        spam_model = json.load(f)
    classifier = gptc.Classifier(spam_model, config["maxNgramLength"])


@cspapi.input
def confidence(message):
    return classifier.confidence(message).get("spam", 0)


@cspapi.action
def log(message, inputs):
    with open(config["spamFile"], "a") as f:
        log_time = str(datetime.datetime.today())
        f.write(",\n")  # append to previous JSON dump, and make this prettier for human eyes
        logEntry = {"time": log_time, "message": message, "confidence": inputs["gptc.confidence"]}
        json.dump(logEntry, f)
