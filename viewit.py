# From https://gist.github.com/glyph/24913ce5c9dac71b7a9c331f2a9d67fc
from ScriptingBridge import SBApplication
from Foundation import NSURL, NSNull

omniFocus = SBApplication.applicationWithURL_(
    NSURL.URLWithString_("file:///Applications/OmniFocus.app")
)

def tasksInView():
    for element in omniFocus.documents()[0].documentWindows()[0].content().leaves():
        yield element.value()

def qualifiedName(aTask):
    def allParents():
        eachTask = aTask
        while eachTask is not None:
            properties = eachTask.properties()
            if properties is not None:
                yield properties.get('name', '?')
                eachTask = properties.get('parentTask')
                if isinstance(eachTask, NSNull):
                    return
    return " / ".join(reversed(list(allParents())))

def main():
    total = 0
    for task in tasksInView():
        estimated = task.estimatedMinutes().get()
        if estimated is not None:
            total += estimated
            print(qualifiedName(task), estimated)
    print("Total Estimated Minutes:", total)

if __name__ == '__main__':
    main()
