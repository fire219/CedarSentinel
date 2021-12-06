import cedarscript.lexer as lexer
import cedarscript.definitions as definitions


def tag(tokens):
    for line in tokens:
        for token in line:
            if token["token"] in definitions.keywords:
                token["tag"] = "keyword"
            elif token["token"] in definitions.inputs:
                token["tag"] = "input"
            elif token["token"] in definitions.actions:
                token["tag"] = "action"
            elif token["token"].replace(".", "0").isnumeric():
                token["tag"] = "number"
                token["token"] = float(token["token"])
            elif token["token"] in "<[{/":
                token["tag"] = "open_compare"
            elif token["token"] in ">]}\\":
                token["tag"] = "close_compare"
            elif token["token"] == "(":
                token["tag"] = "open_paren"
            elif token["token"] == ")":
                token["tag"] = "close_paren"
            elif token["token"].startswith("||||") and len(token["token"]) % 4 == 0:
                token["token"] = len(token["token"]) // 4
                token["tag"] = "indent"

    return tokens


def deindent(lines):
    new_lines = {}
    for number, line in enumerate(lines):
        if not line:
            pass
        elif line[0]["tag"] == "indent":
            new_lines[number] = {
                "indent": line[0]["token"],
                "tokens": line[1:],
                "number": number,
            }
        else:
            new_lines[number] = {"indent": 0, "tokens": line, "number": number}
    return new_lines


def blocks(lines):
    lines = list(lines.values())
    stack = [[]]

    for line in lines:
        if line["tokens"][0]["token"] == "if":
            line["if_true"] = []
            line["if_false"] = []
            stack[-1].append(line)
            stack.append(line["if_true"])
        elif line["tokens"][0]["token"] == "end":
            stack.pop()
        elif line["tokens"][0]["token"] == "else":
            stack.pop()
            stack.append(stack[-1][-1]["if_false"])
        else:
            stack[-1].append(line)

    return stack[-1]


def convert_comparisons(tokens):
    combined = []
    for token in tokens:
        if token["tag"] == "open_compare":
            working = {"type": "comparison", "comparator": token["token"], "values": []}
        elif token["tag"] == "number":
            working["values"].append(token["token"])
        elif token["tag"] == "input":
            working["values"].append(definitions.inputs[token["token"]])
        elif token["tag"] == "close_compare":
            combined.append(
                definitions.Comparison(working["comparator"], working["values"])
            )
        elif token["token"] in ["and", "or"]:
            combined.append(definitions.conjunctions[token["token"]])
        elif token["tag"] in ["open_paren", "close_paren"]:
            combined.append(token["tag"])

    return combined


def assemble_expression(expression):
    out = []
    stack = [out]
    for token in expression:
        if isinstance(token, str):
            if token == "open_paren":
                stack[-1].append([])
                stack.append(stack[-1][-1])
            elif token == "close_paren":
                stack.pop()
        else:
            stack[-1].append(token)
    return out


def gen_ast(lines):
    out = []
    for line in lines:
        command = line["tokens"][0]["token"]
        if command == "if":
            out.append(
                definitions.If(
                    assemble_expression(convert_comparisons(line["tokens"][1:])),
                    gen_ast(line["if_true"]),
                    gen_ast(line["if_false"]),
                )
            )
        elif line["tokens"][0]["tag"] == "input":
            out.append(definitions.inputs[command])
        elif line["tokens"][0]["tag"] == "action":
            out.append(definitions.actions[command])
    return out


def parse(code):
    return gen_ast(blocks(deindent(tag(lexer.lex(code)))))
