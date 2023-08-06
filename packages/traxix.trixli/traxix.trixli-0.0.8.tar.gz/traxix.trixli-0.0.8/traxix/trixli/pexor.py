import json
import ast
from fire import Fire
from traxix.trixli.utils import _f
from functools import partial
from pathlib import Path


def dict_add(d, k, v):

    if k in d:
        d[k].add(v)
    else:
        d[k] = {
            v,
        }


def json_converter(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj


def parser(path, accumulator: list):
    print("path", path)
    try:
        for node in ast.parse(open(path, "r").read()).body:
            if not isinstance(node, ast.ImportFrom) and not isinstance(
                node, ast.Import
            ):
                continue
            for imp in node.names:
                dict_add(accumulator, imp.name, str(path))
            if isinstance(node, ast.ImportFrom):
                dict_add(accumulator, node.module, str(path))
    except FileNotFoundError:
        pass
    except SyntaxError:
        pass


def pexor(p=".", output: str = "/tmp/imports.json", append=True):
    accumulator = {}
    _f("\.py$", p=p, functor=partial(parser, accumulator=accumulator))

    if append:
        old = json.load(open(output, "r"))
        for k, v in old.items():
            if k in accumulator:
                accumulator[k].update(v)
            else:
                accumulator[k] = {
                    v,
                }

    json.dump(accumulator, open(output, "w"), indent=2, default=json_converter)


if __name__ == "__main__":
    Fire(pexor)
