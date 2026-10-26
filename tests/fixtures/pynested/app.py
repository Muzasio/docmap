class Box:
    def start(self):
        def worker():
            self.stop()
        self.after(10, worker)

    def stop(self):
        print("x # not a call(")


def main():
    Box().start()


def walk(items):
    def visit(i):
        if i:
            visit(i - 1)
    visit(items)
