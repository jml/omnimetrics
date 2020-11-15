"""
How to use the new-style APIs until mypy adds support for it:
1. Create a mypy.ini in the root of your project with the following contents:
```
[mypy]
plugins=attrs_ng_plugin.py
```
If you have one, just add the `plugins=` line.
2. Add this file next to the mypy.ini.
3. There is no step 3!
N.B. mypy will treat your classes as `@attr.s(auto_attribs=True)` which means
you MUST use type annotations. This is not how `@attr.define()` et al behave,
they are hybrid.
If you use attrs without type annotions (IOW `attr.ib()`s all the way), you
have to use `attr_class_makers` instead of `attr_dataclass_makers`.
See https://www.attrs.org/en/stable/extending.html#wrapping-the-decorator for
more details.
"""
from mypy.plugin import Plugin
from mypy.plugins.attrs import attr_attrib_makers, attr_dataclass_makers


attr_dataclass_makers.add("attr.define")
attr_dataclass_makers.add("attr.mutable")
attr_dataclass_makers.add("attr.frozen")
attr_attrib_makers.add("attr.field")


class AttrsNGPlugin(Plugin):
    pass


def plugin(version):
    return AttrsNGPlugin
