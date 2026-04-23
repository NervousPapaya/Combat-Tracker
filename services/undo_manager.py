
# The purpose of this manager is to store commands executed for undo and redo actions.

# Right now there is no limit.
class UndoManager:
    def __init__(self, limit=25):
        self.undo_stack = []
        self.redo_stack = []
        #This defines the limit of each stack
        self.limit = limit

    def do(self, command):
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()
        # enforce limit
        if len(self.undo_stack) > self.limit:
            self.undo_stack.pop(0)

    def undo(self):
        if not self.undo_stack:
            return
        cmd = self.undo_stack.pop()
        cmd.undo()
        self.redo_stack.append(cmd)

    def redo(self):
        if not self.redo_stack:
            return
        cmd = self.redo_stack.pop()
        cmd.execute()
        self.undo_stack.append(cmd)