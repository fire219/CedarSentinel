from cedarscript.command_types import Input, Action, CommandList


def initialize(*_, **__):
    pass


def length(message, *_, **__):
    return len(message)


commands = CommandList([Input("length", length)])
