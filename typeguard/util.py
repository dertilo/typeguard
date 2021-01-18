import gzip
import json
import os
import shutil
from dataclasses import dataclass, field, asdict
from typing import Dict, NamedTuple, List, Any

import typing


@dataclass
class CallLog:
    arg2type: Dict[str, str]
    return_type: str
    count: int = 1

    def key(self) -> int:
        return hash((str(self.arg2type), str(self.return_type)))


@dataclass
class TypesLog:
    func_module: str
    qualname: str
    line: int
    call_logs: Dict[str, CallLog] = field(default_factory=dict)

    def key(self) -> str:
        return f"{self.func_module}-{self.qualname}-{self.line}"

    def add_call_log(self, call_log: CallLog):
        if call_log.key() in self.call_logs:
            self.call_logs[call_log.key()].count += 1
        else:
            self.call_logs[call_log.key()] = call_log

    @staticmethod
    def from_dict(d: Dict):
        return TypesLog(
            func_module=d["func_module"],
            qualname=d["qualname"],
            line=d["line"],
            call_logs={i: CallLog(**c) for i, c in d["call_logs"].items()},
        )


TYPEGUARD_CACHE: Dict[str, TypesLog] = {}


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
        return module + "." + o.__class__.__name__


def get_nested_type(x: Any, in_generator=False):
    if x.__class__.__name__ == "tuple" and len(x) <= 5:
        lisst = f"[{','.join([get_nested_type(t) for t in x])}]"
        annotation = f"typing.Tuple{lisst}"
    elif x.__class__.__name__ == "list":
        common_type = get_common_type(x)
        annotation = f"typing.List[{common_type}]"
    elif x.__class__.__name__ == "dict":
        key_type = get_common_type(x.keys())
        val_type = get_common_type(x.values())
        atleast_one_is_not_any = any([t != "typing.Any" for t in [key_type, val_type]])
        if atleast_one_is_not_any:
            ann = f"typing.Dict[{key_type},{val_type}]"
        else:
            ann = "typing.Dict"
        annotation = ann
    else:
        annotation = get_module_name(x)
    if in_generator:
        annotation = f"typing.Generator[{annotation},None,None]"
    return annotation


def get_typing_type(type_name: str):
    potential_typing_type = type_name.capitalize()
    if hasattr(typing, potential_typing_type):
        return getattr(typing, potential_typing_type)
    else:
        return type_name


def get_common_type(variables: List[Any]):
    types = [get_typing_type(get_module_name(t)) for t in variables]
    if len(set(types)) == 1:
        ttype = types[0]
    else:
        ttype = "typing.Any"
    return ttype


def unwanted(func):
    if func.__module__.startswith("namedtuple") and func.__name__.endswith("__new__"):
        is_unwanted = True
    else:
        is_unwanted = False
    return is_unwanted


def log_fun_call(func, memo, retval, in_generator=False):
    global TYPEGUARD_CACHE

    if not unwanted(func):
        add_to_cache(TYPEGUARD_CACHE, func, in_generator, memo, retval)


def add_to_cache(TYPEGUARD_CACHE, func, in_generator, memo, retval):
    call_log = CallLog(
        arg2type={k: get_nested_type(v) for k, v in memo.arguments.items()},
        return_type=get_nested_type(retval, in_generator),
    )
    types_log = TypesLog(
        func.__module__, func.__qualname__, func.__code__.co_firstlineno
    )
    if types_log.key() not in TYPEGUARD_CACHE:
        TYPEGUARD_CACHE[types_log.key()] = types_log
    TYPEGUARD_CACHE[types_log.key()].add_call_log(call_log)
