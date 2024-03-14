import cspapi
import gptc
import sqlite3
from . import server
import threading


@cspapi.init
def initialize():
    global classifier
    try:
        open(config["database"]).close()
        exists = True
    except FileNotFoundError:
        exists = False
    con = sqlite3.connect(config["database"])
    if not exists:
        con.execute(
            "CREATE TABLE log (id integer PRIMARY KEY, message text, category text);"
        )
        con.commit()

    cur = con.cursor()
    cur.execute(
        "SELECT category, message FROM log WHERE category='good' OR category='spam';"
    )

    model = [{"category": line[0], "text": line[1]} for line in cur.fetchall()]

    con.close()

    compiled_model = gptc.compile(model, config["maxNgramLength"])
    classifier = gptc.Classifier(compiled_model, config["maxNgramLength"])
    server.config = config
    threading.Thread(target=server.run, daemon=True).start()


@cspapi.input
def confidence(message):
    return classifier.confidence(message).get("spam", 0)


def _log(message, category):
    con = sqlite3.connect(config["database"])
    cur = con.cursor()
    cur.execute(
        "INSERT INTO log (message, category) VALUES (?, ?);",
        (message, category),
    )
    con.commit()
    con.close()


@cspapi.action
def log_good(message):
    _log(message, "good")


@cspapi.action
def log_prob_good(message):
    _log(message, "probably_good")


@cspapi.action
def log_unknown(message):
    _log(message, "unknown")


@cspapi.action
def log_prob_spam(message):
    _log(message, "probably_spam")


@cspapi.action
def log_spam(message):
    _log(message, "spam")
