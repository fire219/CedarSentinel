from cedarscript.command_types import Input, Action, CommandList

def initialize(*_, **__):
    pass

commands = CommandList([
    Action("delete", initialize),
    ])
