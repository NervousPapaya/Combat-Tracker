class Command:
    def execute(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError