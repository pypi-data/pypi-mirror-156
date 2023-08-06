from io import TextIOWrapper
from .Directory import Directory
from .Block import Block
from .btype import DIR, FILE, __BaseType__
import json

def get_path(children:Directory, force_abs=False):
    """返回Children内所有block的路径"""
    if force_abs:
        res = children.map(lambda x: x.abspath)
    else:
        res = children.map(lambda x: x.path)
    return res

def type_filter(children:Directory, __type:__BaseType__)->Directory:
    def dfs(x):
        return Directory([
            dfs(cell) if hasattr(cell, "__iter__") else cell
            for cell in x
            if hasattr(cell, "__iter__") or (type(cell)==Block and cell.btype==__type)
        ], copy=False)
    return dfs(children)

def file_filter(children:Directory)->Directory:
    """返回Children中的所有FILE类型Block"""
    res = type_filter(children, FILE)
    return res

def dir_filter(children:Directory)->Directory:
    """返回Children中的所有DIR类型Block"""
    res = type_filter(children, DIR)
    return res

def extension_filter(dir:Directory, *extensions):
    def dfs(x: Directory):
        return Directory([
            dfs(cell) if hasattr(cell, "__iter__") else cell
            for cell in x
            if hasattr(cell, "__iter__") or (type(cell)==Block and cell.extension in extensions)
        ], copy=False)
    return dfs(dir)

def remove(target:Directory):
    if type(target) == Directory:
        target.map(lambda x: x.remove())
    elif type(target) == Block:
        target.remove()
    else:
        raise ValueError(target," cannot be removed!")


def save_json(obj, fp, encoding="utf8", indent=None, ensure_ascii=False):
    t = type(fp)
    
    if t == str:
        f = open(fp, 'w+', encoding=encoding)
        fp = f
    elif t != TextIOWrapper:
        raise ValueError("`fp`: except TextIOWrapper|str, got", t)

    json.dump(obj, fp, ensure_ascii=ensure_ascii, indent=indent)