import cspapi
import datetime
import gptc
import json
import sqlite3


@cspapi.init
def initialize():
    global classifier, con
    try:
        open(config["database"]).close()
        exists = True
    except FileNotFoundError:
        exists = False
    con = sqlite3.connect(config["database"])
    if not exists:
        con.execute("CREATE TABLE log (id integer PRIMARY KEY, time integer, message text, category text);")
        con.commit()
    cur = con.cursor()
    cur.execute("SELECT category, message FROM log WHERE category='good' OR category='spam';")
    model = [{"category": line[0], "text": line[1]} for line in cur.fetchall()]
    compiled_model = gptc.compile(model, config["maxNgramLength"])
    classifier = gptc.Classifier(compiled_model, config["maxNgramLength"])


@cspapi.input
def confidence(message):
    return classifier.confidence(message).get("spam", 0)


def _log(message, category):
    log_time = str(datetime.datetime.today())
    cur = con.cursor()
    cur.execute("INSERT INTO log (time, message, category) VALUES (?, ?, ?);", (log_time, message, category))
    con.commit()


@cspapi.action
def loggood(message):
    _log(message, "good")


@cspapi.action
def logprobgood(message):
    _log(message, "probably_good")


@cspapi.action
def logunknown(message):
    _log(message, "unknown")


@cspapi.action
def logprobspam(message):
    _log(message, "probably_spam")


@cspapi.action
def logspam(message):
    _log(message, "spam")
