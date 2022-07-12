keywords = ["if", "else", "end", "and", "or"]


class CodePiece:
    pass


class If(CodePiece):
    def __init__(self, condition, if_true, if_false):
        self.condition = condition
        self.if_true = if_true
        self.if_false = if_false

    def __repr__(self):
        return f"If({self.condition}, {self.if_true}, {self.if_false})"


class Identifier(CodePiece):
    _type = "Identifier"

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"{self._type}('{self.name}')"


class Conjunction(Identifier):
    _type = "Conjunction"


conjunctions = {
    "and": Conjunction("and"),
    "or": Conjunction("or"),
}

comparators = {
    "<": "<",
    "[": "<=",
    "{": "==",
    "/": "!=",
}


class Comparison(CodePiece):
    def __init__(self, comparator, values):
        self.values = values
        self.comparator = comparators[comparator]

    def __repr__(self):
        combined = f" {self.comparator} ".join([repr(value) for value in self.values])
        return f"Comparison({combined})"


class CedarScriptSyntaxError(BaseException):
    pass
