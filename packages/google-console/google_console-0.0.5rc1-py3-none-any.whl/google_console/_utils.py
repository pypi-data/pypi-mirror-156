import sys


def __silent(function, silent: bool = True):
    stdout = sys.stdout
    if silent:
        sys.stdout = None
    function()
    sys.stdout = stdout
