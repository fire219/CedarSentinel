import dataclasses
from types import FunctionType
from typing import Union


@dataclasses.dataclass
class CodePiece:
    pass


@dataclasses.dataclass
class Boolean(CodePiece):
    pass


@dataclasses.dataclass
class Block(CodePiece):
    items: list

    def __call__(self, inputs):
        actions = set()
        for item in self.items:
            actions = actions.union(item(inputs))
        return actions


@dataclasses.dataclass
class Instruction(CodePiece):
    pass


@dataclasses.dataclass
class Action(Instruction):
    name: str

    def __call__(self, inputs):
        return {
            self.name,
        }


@dataclasses.dataclass
class IfStatement(Instruction):
    condition: Boolean
    true_block: Block
    false_block: Instruction

    def __call__(self, inputs):
        if self.condition(inputs):
            return self.true_block(inputs)
        else:
            return self.false_block(inputs)


@dataclasses.dataclass
class Number(CodePiece):
    pass


@dataclasses.dataclass
class Constant(Number):
    value: int

    def __call__(self, inputs):
        return self.value


@dataclasses.dataclass
class Input(Number):
    name: str

    def __call__(self, inputs):
        return inputs[self.name]


@dataclasses.dataclass
class Operator(CodePiece):
    name: str
    function: dataclasses.InitVar[FunctionType]

    def __post_init__(self, function):
        self.function = function

    def __call__(self, a, b):
        return self.function(a, b)


@dataclasses.dataclass
class ComparisonOperator(Operator):
    pass


comparison_operators = {
    "<": ComparisonOperator("<", lambda x, y: x < y),
    "<=": ComparisonOperator("<=", lambda x, y: x <= y),
    "==": ComparisonOperator("==", lambda x, y: x == y),
    "!=": ComparisonOperator("!=", lambda x, y: x != y),
    ">=": ComparisonOperator(">=", lambda x, y: x >= y),
    ">": ComparisonOperator(">", lambda x, y: x > y),
}


@dataclasses.dataclass
class Comparison(Boolean):
    arg_a: Number
    operator: ComparisonOperator
    arg_b: Number

    def __call__(self, inputs):
        return self.operator(self.arg_a(inputs), self.arg_b(inputs))


@dataclasses.dataclass
class CombinationOperator(Operator):
    pass


combination_operators = {
    "and": CombinationOperator("and", lambda x, y: x and y),
    "or": CombinationOperator("and", lambda x, y: x or y),
}


@dataclasses.dataclass
class Combination(Boolean):
    arg_a: Number
    operator: CombinationOperator
    arg_b: Number

    def __call__(self, inputs):
        return self.operator(self.arg_a(inputs), self.arg_b(inputs))


@dataclasses.dataclass
class Inversion(Boolean):
    value: Boolean

    def __call__(self, inputs):
        return not self.value(inputs)
