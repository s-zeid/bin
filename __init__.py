#!/usr/bin/env python3

import importlib
import importlib.util
import os
import re
import subprocess
import sys
import types

from typing import *


ROOT = os.path.abspath(os.path.dirname(__file__))


class ShellScript:
  def __init__(self, filename: str):
    self.filename = filename

  def __call__(self, *argv: str | list[str] | tuple[str, ...]) -> int:
    if len(argv) == 1 and isinstance(argv[0], (list, tuple)):
      argv_list = list(argv[0])
    else:
      argv_list = list(cast(tuple[str, ...], argv))
    return self.Popen(argv_list).wait()

  def Popen(self, argv: list[str], *popen_args, **popen_kwargs) -> subprocess.Popen:
    argv = fix_argv(argv, self.filename)
    popen_kwargs = popen_kwargs.copy()
    popen_kwargs["executable"] = self.filename
    return subprocess.Popen(argv, *popen_args, **popen_kwargs)


class MainWrapper:
  class MainProtocol(Protocol):
    def __call__(self, argv: list[str], *args, **kwargs) -> int | None:
      ...

  def __init__(self, real_main: MainProtocol, filename: str):
    self.real_main = real_main
    self.filename = filename

  def __call__(self, argv: list[str] | None = None, *args, **kwargs) -> int:
    result = self.real_main(fix_argv(argv, self.filename), *args, **kwargs)
    return result if isinstance(result, int) else 0


def fix_argv(argv: list[str] | tuple[str, ...] | None, filename: str) -> list[str]:
  if not isinstance(argv, (list, tuple)) or len(argv) == 0:
    argv = [""]
  else:
    argv = list(argv[:])

  if not argv[0] or not isinstance(argv[0], str):
    argv[0] = filename

  return argv


def load_script(script: str, name: str = "") -> types.ModuleType:
  if not name:
    name = os.path.basename(script).replace("-", "_")

  path = os.path.abspath(os.path.join(ROOT, script))

  if is_python3(path):
    dont_write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
      loader = importlib.machinery.SourceFileLoader(name, path)
      spec = importlib.util.spec_from_loader(name, loader)
      if spec is None:
        raise ModuleNotFoundError("no script named '{script}'")
      module = importlib.util.module_from_spec(spec)
      loader.exec_module(module)
    finally:
      sys.dont_write_bytecode = dont_write_bytecode
    module.__file__ = module.__file__ or path
    if callable(getattr(module, "main", None)):
      setattr(module, "main", MainWrapper(module.main, module.__file__))
  else:
    module = types.ModuleType(name)
    module.__file__ = path
    setattr(module, "main", ShellScript(module.__file__))
    sys.modules[name] = module

  return module


def find_scripts() -> list[str]:
  return [
    filename for filename in sorted(os.listdir(ROOT))
    if "." not in filename and not os.path.isdir(os.path.join(ROOT, filename))
  ]


def find_no_main() -> list[str]:
  result = []

  for script in find_scripts():
    path = os.path.join(ROOT, script)
    if not is_python3(path):
      continue
    with open(path, "rb") as f:
      if not re.search(rb"^def main\(argv", f.read(), re.MULTILINE):
        result += [script]

  return result


def is_python3(script: str) -> bool:
  with open(script, "rb") as f:
    shebang = f.readline()
    if shebang.startswith(b"#!") and b"python" in shebang and not b"python2" in shebang:
      return True
  return False


def main(argv: list[str]) -> int:
  prog = os.path.basename(argv[0])
  prog = prog if prog != "__main__.py" else __package__ or __name__

  if len(argv) < 2:
    print(f"Usage: {prog} {{script [args]|--no-main}}", file=sys.stderr)
    return 2

  if argv[1] == "--no-main":
    for script in find_no_main():
      print(script)
    return 0

  return load_script(argv[1]).main(argv[1:])


if __name__ == "__main__":
  try:
    sys.exit(main(sys.argv))
  except KeyboardInterrupt:
    pass
