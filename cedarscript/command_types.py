import dataclasses
import types


@dataclasses.dataclass
class Command:
    function: types.FunctionType
    name: str


class Input(Command):
    pass


class Action(Command):
    pass


@dataclasses.dataclass
class CommandList:
    commands: list[Command]

    def to_dict(self):
        return {command.name: command for command in self.commands}
