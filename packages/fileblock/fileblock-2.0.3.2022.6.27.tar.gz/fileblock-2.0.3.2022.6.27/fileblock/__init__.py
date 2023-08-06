from .Block import Block
from .Directory import Directory
from .btype import FILE, DIR
from .utils import *
def make_children(*child) -> Directory:
    return Directory.make(child)

def unfold(*iter):
    def fn(iter):
        res = Directory(copy=False)
        for cell in iter:
            if hasattr(cell, "__iter__"):
                res += fn(cell)
            else:
                res.append(cell)
        return res
    return fn(iter)

