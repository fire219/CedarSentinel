import cedarscript.definitions as definitions

def split(code):
    code = code.lower()

    tokens = [""]
    indices = [[]]

    for index, char in enumerate(code.replace("    ", "||||")):
        if char in "abcdefghijklmnopqrstuvwxyz":
            if not tokens[-1].isalpha():
                tokens.append("")
                indices.append([])
            tokens[-1] += char
            indices[-1].append(index)
        elif char in "0123456789.":
            if not tokens[-1].replace(".", "0").isnumeric():
                tokens.append("")
                indices.append([])
            tokens[-1] += char
            indices[-1].append(index)
        elif char in "<>[]{}()/\:\n":
            tokens.append(char)
            indices.append([index])
            tokens.append("")
            indices.append([])
        elif char == "|":
            if tokens[-1].replace("|", "") == "" and tokens[-2] == "\n":
                tokens[-1] += "|"
                indices[-1].append(index)
        elif char == " ":
            tokens.append("")
            indices.append([])
        elif not (char == '_' and tokens[-1].isalpha()):
            raise definitions.CedarScriptSyntaxError(f'invalid character: `{char}`')
    return tokens, indices


def compress(tokens, indices):
    tokens = [token for token in tokens if token]
    indices = [[min(index), max(index)] for index in indices if index]
    return tokens, indices


def combine(tokens, indices):
    return [
        {"token": token, "location": location}
        for token, location in zip(tokens, indices)
    ]


def lineify(tokens):
    lines = [[]]
    for token in tokens:
        lines[-1].append(token)
        if token["token"] == "\n":
            lines.append([])

    start = 0
    for line in lines:
        if not line:
            continue

        for token in line:
            token["location"][0] -= start
            token["location"][1] -= start

        start = line[-1]["location"][0] + 1
        del line[-1]

    return lines


def lex(code):
    return lineify(combine(*compress(*split(code))))
