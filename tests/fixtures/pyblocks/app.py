def load(path):
    try:
        class Reader:
            pass

        def opener():
            return Reader()
    except ImportError:
        return None
    if path:
        def check():
            return opener()
        return check()
    return opener()


def run(items):
    for i in items:
        def show():
            return i
        show()
