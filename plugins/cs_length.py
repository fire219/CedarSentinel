from cedarscript.command_types import Input, Action, CommandList

def initialize(_config, *_, **__):
    pass

def length(message, *_, **__):
    return len(message)

commands = CommandList([Input("length", length)])
