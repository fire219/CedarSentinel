from cedarscript.decorators import input, action, init


@init
def initialize(*_, **__):
    pass


@input
def length(message):
    return len(message)
