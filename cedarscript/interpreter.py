import cedarscript.definitions as definitions
import cedarscript.parser as parser


class Interpreter:
    def __init__(self, code):
        self.code = parser.parse(code)

    def interpret(self, confidence, length, reputation):
        inputs = {
            "confidence": confidence,
            "length": length,
            "reputation": reputation,
        }
        return self.interpret_block(self.code, inputs)

    def interpret_block(self, code, inputs):
        actions = set()
        for statement in code:
            if isinstance(statement, definitions.Action):
                actions.add(statement.name)
            elif isinstance(statement, definitions.If):
                if self.interpret_expression(statement.condition, inputs):
                    block_actions = self.interpret_block(statement.if_true, inputs)
                else:
                    block_actions = self.interpret_block(statement.if_false, inputs)

                actions = set(
                    (
                        *actions,
                        *block_actions,
                    )
                )
        return actions

    def evaluate(self, token, inputs):
        if isinstance(token, float):
            return token
        elif isinstance(token, definitions.Input):
            return inputs[token.name]

    def interpret_expression(self, expression, inputs):
        if isinstance(expression, definitions.Comparison):
            values = [self.evaluate(token, inputs) for token in expression.values]
            comparator = {
                "<": (lambda x, y: x < y),
                "<=": (lambda x, y: x <= y),
                "==": (lambda x, y: x == y),
                "!=": (lambda x, y: x != y),
            }[expression.comparator]

            tests = []

            while len(values) >= 2:
                tests.append(comparator(*values[0:2]))
                values.pop(0)

            return all(tests)
        elif isinstance(expression, list):
            expressions = [
                self.interpret_expression(e, inputs) for e in expression[::2]
            ]
            conjunctions = [
                {"and": (lambda x, y: x and y), "or": (lambda x, y: x or y)}[e.name]
                for e in expression[1::2]
            ]

            state = expressions.pop(0)

            while conjunctions:
                state = conjunctions.pop(0)(state, expressions.pop(0))

            return state
        elif isinstance(expression, definitions.Input):
            return inputs[expression.name]
