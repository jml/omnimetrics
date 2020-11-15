"""Dump Omnifocus database to JSON.

Author: Glyph Lefkowitz
Source: https://gist.github.com/glyph/e51d1809bf1edcb5e8f5dceb48f99ccb
"""

from datetime import datetime
from json import dumps

from aeosa.appscript import app, k, reference

omniFocus = app("OmniFocus")


def jsonify(o):
    if isinstance(o, reference.Reference):
        return str(o.id())
    elif isinstance(o, datetime):
        return o.isoformat()
    if isinstance(o, type(k.task)):
        return o.name
    return o


def fixkeys(d):
    if isinstance(d, dict):
        return {
            (key.name if isinstance(key, type(k.task)) else key): (
                fixkeys(v) if v != k.missing_value else None
            )
            for key, v in d.items()
        }
    else:
        return d


def main():
    first = True
    print("[")
    for task in omniFocus.default_document.flattened_tasks():
        if first:
            first = False
        else:
            print(",")
        value = fixkeys(task.properties())
        print(dumps(value, default=jsonify,))
    print("]")
