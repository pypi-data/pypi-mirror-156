from . import time_def_ as td

__all__ = ("time_def",)

def time_def(func):
    return td.time_def_(func)