"""Interface to an OmniFocus database.

Original code by Glyph Lefkowitz

Source:

- https://gist.github.com/glyph/e51d1809bf1edcb5e8f5dceb48f99ccb
- https://gist.github.com/glyph/24913ce5c9dac71b7a9c331f2a9d67fc
"""
from pprint import pprint
from typing import Any, Iterable

import attr
from Foundation import NSURL
from ScriptingBridge import SBApplication

OMNIFOCUS = SBApplication.applicationWithURL_(
    NSURL.URLWithString_("file:///Applications/OmniFocus.app")
)

TASK_CLASS = OMNIFOCUS.classForScriptingClass_("task")


@attr.frozen
class Task:
    id: str


def load_tasks(omni_database: Any) -> Iterable[Task]:
    for task in omni_database.flattenedTasks():
        properties = task.properties()
        try:
            yield Task(id=properties["id"])
        except KeyError:
            pprint(properties)
            raise
