from random import random
import json
from . import Block
from .btype import __BaseType__

def deep_maker(x):
    if hasattr(x, "__iter__"):
        res = []
        for cell in x:
            res.append(deep_maker(cell))
        return Directory(res, copy=False, deep_make=False)
    else:
        return x


class Directory:

    def __init__(self, data=[], copy=True, deep_make=False):
        if isinstance(data, Directory):
            data = data.data
        if deep_make:
            data = deep_maker(data)
        if copy:
            self.data = data.copy()
        else:
            self.data = data


    def map(self, fn):
        def dfs(x):
            return Directory([
                dfs(cell) if isinstance(cell, Directory) else fn(cell)
                for cell in x
            ], copy=False, deep_make=False)
        return dfs(self)


    def to_json(self, fpath: str, file_only=False, dir_only=False, abspath = False, indent=None, encoding="utf8"):
        """
            注: 若file_only 和 dir_only 同时为 True 则 全都输出.

            tips: if `file_only` == `dir_only` == True,
                    then output is all.
        """
        def convert(child):
            if type(child) == Directory:
                res = []
                for c in child:
                    tmp = convert(c)
                    if tmp:
                        res.append(tmp)
                return res
            if file_only and not dir_only:
                if child.isfile:
                    return child.abstract(abspath).__dict__
            elif dir_only and not file_only:
                if child.isdir:
                    return child.abstract(abspath).__dict__
            else:
                return child.abstract(abspath).__dict__

        data = convert(self)
        with open(fpath, "w+", encoding=encoding) as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        

    def unfold(self):
        def proc(children, out):
            if isinstance(children, Directory):
                for cell in children:
                    proc(cell, out)
            else:
                out.append(children)
        res = []
        proc(self.data, res)
        return Directory(res, copy=False, deep_make=False)


    def copy(self):
        return Directory(self.data, copy=True, deep_make=False)


    def shuffle(self):
        res = self.copy()
        le = res.__len__()
        for i in range(1, le+1):
            idx = int(random() * (le - i))
            res[idx], res[le - i] = res[le - i], res[idx]
        return res
    

    def append(self, obj):
        self.data.append(obj)
        return self


    def extend(self, obj):
        self.data.extend(obj)
        return self
    

    def remove(self, x):
        self.data.remove(x)
        return self


    def pop(self, idx):
        return self.data.pop(idx)
    
    def extension_filter(self, *extensions):
        rep_ext = [ 
            '.' + e
            for e in extensions
            if e[0] != '.'
        ]
        def dfs(x: Directory):
            return Directory([
                dfs(cell) if hasattr(cell, "__iter__") else cell
                for cell in x
                if hasattr(cell, "__iter__") or
                    (type(cell) == Block.Block and
                    (cell.extension in extensions or cell.extension in rep_ext))
            ], copy=False, deep_make=False)
        return dfs(self)
            

    @staticmethod
    def make(*child, copy=True, deep_make=True):
        def proc(children):
            if hasattr(children[0], "__iter__"):
                res = Directory(copy=False, deep_make=False)
                for child in children:
                    res.append(proc(child))
                return res
            return Directory(children, copy=copy, deep_make=deep_make)
        return proc(child)

    @property
    def abspaths(self):
        return Directory([child.abspath for child in self], copy=False, deep_make=False)
    
    @property
    def super_dir_names(self):
        return self.map(lambda x: x.super_dir_name)

    
    def __add__(self, x):
        return Directory(self.data + x, copy=False, deep_make=False)
    

    def __len__(self):
        return self.data.__len__()
    

    def __iter__(self):
        return self.data.__iter__()
    
    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return Directory(self.data[idx], copy=False, deep_make=False)
        return self.data[idx]

    def __setitem__(self, k, v):
        self.data[k] = v
        return self

    def __str__(self) -> str:
        return str(self.data)
    

    def __repr__(self) -> str:
        return self.__str__()

if __name__  == "__main__":

    c = Directory([1, 2, 3])
    x = c + Directory([2, 3, 4])
    print(x)
    