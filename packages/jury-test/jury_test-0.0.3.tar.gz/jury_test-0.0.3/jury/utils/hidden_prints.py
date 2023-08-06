import sys
from io import StringIO


class HiddenPrints:
    def __init__(self, activated=True):
        self.activated = activated
        self.io = StringIO()
        self.old_io = sys.__stdout__

    def __enter__(self):
        self.old_io = sys.stdout
        if self.activated:
            sys.stdout = self.io
        else:
            sys.stdout = sys.__stdout__
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.old_io

    def get_output(self):
        return self.io.getvalue()

    @staticmethod
    def recover_stdout():
        sys.stdout = sys.__stdout__
