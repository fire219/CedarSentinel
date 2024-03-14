from lark import Lark, Transformer
from pathlib import Path
from cedarscript.transformer import CedarScriptTransformer

with open(Path(__file__).parent / "grammar.lark") as f:
    parser = Lark(f.read(), start="block")


def load(script):
    return CedarScriptTransformer().transform(parser.parse(script))
