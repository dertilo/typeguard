import gzip
import json
import os
import shutil
from typing import Dict, NamedTuple

class TypesLog(NamedTuple):
    func_module:str
    qualname:str
    arg2type:Dict[str,str]
    return_type:str

    def __hash__(self) -> int:
        return hash(str(self))


def write_json_line(file: str, datum: Dict, mode="wb"):
    with gzip.open(file, mode=mode) if file.endswith("gz") else open(
        file, mode=mode
    ) as f:
        line = f"{json.dumps(datum, skipkeys=True, ensure_ascii=False)}\n"
        if "b" in mode:
            line = line.encode("utf-8")
        f.write(line)

def get_module_name(o):
  # o.__module__ + "." + o.__class__.__qualname__ is an example in
  # this context of H.L. Mencken's "neat, plausible, and wrong."
  # Python makes no guarantees as to whether the __module__ special
  # attribute is defined, so we take a more circumspect approach.
  # Alas, the module name is explicitly excluded from __qualname__
  # in Python 3.

  module = o.__class__.__module__
  if module is None or module == str.__class__.__module__:
    return o.__class__.__name__  # Avoid reporting __builtin__
  else:
    return module + '.' + o.__class__.__name__


def get_module_names(x):
    if x.__class__.__name__ == "tuple" and len(x)<=5:
        lisst = f"[{','.join([get_module_name(t) for t in x])}]"
        return f"Tuple{lisst}"
    elif x.__class__.__name__ == "list":
        types = [get_module_name(t) for t in x]
        if len(set(types))==1:
            t = types[0]
            return f"List[{t}]"
        else:
            return get_module_name(x)
    elif x.__class__.__name__ == "dict":
        key_type = get_type(x.keys())
        val_type = get_type(x.values())
        if any([t != "Any" for t in [key_type,val_type]]):
            ann = f"Dict[{key_type},{val_type}]"
        else:
            ann = "Dict"
        return ann
    else:
        return get_module_name(x)


def get_type(variables):
    types = [get_module_name(t) for t in variables]
    if len(set(types)) == 1:
        ttype = types[0]
    else:
        ttype = "Any"
    return ttype