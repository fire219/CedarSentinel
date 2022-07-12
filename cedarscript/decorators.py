from cedarscript.command_types import Input, Action
import dataclasses
import inspect
import types


@dataclasses.dataclass
class TolerantFunction:
    function: types.FunctionType

    def __post_init__(self):
        self.accepted = inspect.signature(self.function).parameters

    def __call__(self, **kwargs):
        new_kwargs = {key: value for key, value in kwargs.items() if key in self.accepted}
        return self.function(**new_kwargs)


def init(function):
    return TolerantFunction(function)


def input(function):
    return Input(function.__name__, TolerantFunction(function))


def action(function):
    return Action(function.__name__, TolerantFunction(function))
