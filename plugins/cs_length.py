import cspapi


@cspapi.init
def initialize():
    pass


@cspapi.input
def length(message):
    return len(message)
