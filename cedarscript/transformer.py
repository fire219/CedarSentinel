import lark
import cedarscript.code_classes as code_classes


def passthrough(self, children):
    return children[0]


class CedarScriptTransformer(lark.Transformer):
    def COMPARISON_OPERATOR(self, children):
        return code_classes.comparison_operators[str(children)]

    def COMBINATION_OPERATOR(self, children):
        return code_classes.combination_operators[str(children)]

    def NUMBER(self, children):
        return float(children)

    def IDENTIFIER(self, children):
        return str(children)

    def block(self, children):
        return code_classes.Block(children)

    def action(self, children):
        return code_classes.Action(children[0])

    def if_statement(self, children):
        condition = children[0]
        true_block = children[1]
        try:
            false_block = children[2]
        except IndexError:
            false_block = code_classes.Block([])
        return code_classes.IfStatement(condition, true_block, false_block)

    def value(self, children):
        return children[0]

    def constant(self, children):
        return code_classes.Constant(children[0])

    def input(self, children):
        return code_classes.Input(children[0])

    def condition(self, children):
        return children[0]

    def comparison(self, children):
        return code_classes.Comparison(children[0], children[1], children[2])

    def combination(self, children):
        return code_classes.Combination(children[0], children[1], children[2])

    def inversion(self, children):
        return code_classes.Inversion(children[0])
