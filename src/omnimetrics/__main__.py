from ._procrastinatron import attempt, tasksInView


def procrastinatron():
    print(attempt(next(tasksInView())))
