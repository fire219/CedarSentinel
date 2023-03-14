import cspapi
import profanity_check

@cspapi.init
def initialize():
    pass


def apply_allowlist(message, allowlist):
    if allowlist:
        return apply_allowlist(message.lower().replace(allowlist[0], ""), allowlist[1:])
    else:
        return message


@cspapi.input
def confidence(message):
    return profanity_check.predict_prob([apply_allowlist(message, config["allowlist"])])[0]
