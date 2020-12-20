import gzip
import json
from typing import Dict, NamedTuple


def write_json(file: str, datum: Dict, mode="wb"):
    with gzip.open(file, mode=mode) if file.endswith("gz") else open(
        file, mode=mode
    ) as f:
        line = json.dumps(datum, skipkeys=True, ensure_ascii=False)
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

# class TypesLog(NamedTuple):