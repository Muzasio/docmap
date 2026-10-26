class Outer:
    class Inner:
        def ping(self):
            return 1

    def go(self):
        return self.close()

    def close(self) -> None: self.reset()

    def reset(self):
        pass


class Other:
    def close(self):
        pass


def test():
    class FW:
        def run(self):
            pass
    return FW()
