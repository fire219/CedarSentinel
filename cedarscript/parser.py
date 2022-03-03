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
            else:
                raise definitions.CedarScriptSyntaxError(
                    f'unrecognized token: {token["token"]}'
                )

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
            if len(stack) == 0:
                raise definitions.CedarScriptSyntaxError(
                    f"`end` outside an `if`/`else` statement"
                )
        elif line["tokens"][0]["token"] == "else":
            stack.pop()
            if len(stack) == 0:
                raise definitions.CedarScriptSyntaxError(
                    f"`else` outside an `if` statement"
                )
            stack.append(stack[-1][-1]["if_false"])
        else:
            stack[-1].append(line)

    return stack[-1]


def convert_comparisons(tokens):
    combined = []
    for token in tokens:
        if token["tag"] == "open_compare":
            if "working" in locals():
                raise definitions.CedarScriptSyntaxError("comparisons cannot be nested")
            working = {"type": "comparison", "comparator": token["token"], "values": []}
        elif token["tag"] == "number":
            try:
                working["values"].append(token["token"])
            except (NameError, UnboundLocalError):
                raise definitions.CedarScriptSyntaxError("number outside comparison")
        elif token["tag"] == "input":
            try:
                working["values"].append(definitions.inputs[token["token"]])
            except (NameError, UnboundLocalError):
                raise definitions.CedarScriptSyntaxError("input outside comparison")
        elif token["tag"] == "close_compare":
            try:
                combined.append(
                    definitions.Comparison(working["comparator"], working["values"])
                )
            except (NameError, UnboundLocalError):
                raise definitions.CedarScriptSyntaxError(
                    f'closing comparator `{token["token"]}` without matching opening comparator'
                )
            del working
        elif token["token"] in ["and", "or"]:
            combined.append(definitions.conjunctions[token["token"]])
        elif token["tag"] in ["open_paren", "close_paren"]:
            combined.append(token["tag"])
        else:
            raise definitions.CedarScriptSyntaxError(
                f'invalid token in boolean expression: {token["token"]}'
            )

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
                if len(stack) == 0:
                    raise definitions.CedarScriptSyntaxError(
                        f"`)` without matching `(`"
                    )
        else:
            stack[-1].append(token)
    if len(stack) != 1:
        raise definitions.CedarScriptSyntaxError(f"`(` without matching `)`")
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
