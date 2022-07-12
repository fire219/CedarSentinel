import dataclasses
import types


@dataclasses.dataclass
class Command:
    name: str
    function: types.FunctionType

    def prefix(self, namespace):
        return type(self)(f"{namespace}.{self.name}", self.function)


class Input(Command):
    pass


class Action(Command):
    pass


class CommandList(list):
    def to_dict(self):
        return {command.name: command for command in self}
    
    def _only_type(self, item_type):
        return CommandList(item for item in self if isinstance(item, item_type))

    @property
    def inputs(self):
        return self._only_type(Input)

    @property
    def actions(self):
        return self._only_type(Action)

    def prefix(self, namespace):
        return CommandList(command.prefix(namespace) for command in self)

    @property
    def names(self):
        return [item.name for item in self]
