#!/usr/bin/env python3

import importlib.machinery
import importlib.util
import os
import re
import subprocess
import sys
import types

from typing import *


ROOT = os.path.abspath(os.path.dirname(__file__))


class ScriptProtocol(Protocol):
  main: "MainProtocol"

  class MainProtocol(Protocol):
    def __call__(self, argv: list[str], *args, **kwargs) -> int: ...


class Script:
  def __init__(self, name: str):
    self.name = os.path.basename(name)
    self.path = os.path.abspath(os.path.join(ROOT, name))
    if not os.path.isfile(self.path):
      raise ModuleNotFoundError("no script named '{self.name}'")

  def __repr__(self):
    return f"<Script name={self.name!r} path={self.path!r}>"

  def load(self, module_name: str | None = None) -> ScriptProtocol:
    if not module_name:
      module_name = os.path.basename(self.name).replace("-", "_")

    module: ScriptProtocol

    if self.is_python3():
      dont_write_bytecode = sys.dont_write_bytecode
      sys.dont_write_bytecode = True
      try:
        loader = importlib.machinery.SourceFileLoader(module_name, self.path)
        spec = importlib.util.spec_from_loader(module_name, loader)
        if not spec:
          raise ImportError(f"BUG while loading '{self.name}'")
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
      finally:
        sys.dont_write_bytecode = dont_write_bytecode
      module.__file__ = module.__file__ or self.path
      if callable(getattr(module, "main", None)):
        setattr(module, "main", PythonMainWrapper(module.__file__, module.main))
    else:
      module = types.ModuleType(module_name)
      module.__file__ = self.path
      setattr(module, "main", ShellMainWrapper(module.__file__))

    if module_name not in sys.modules:
      sys.modules[module_name] = cast(types.ModuleType, module)
    return module

  def is_python3(self) -> bool:
    with open(self.path, "rb") as f:
      shebang = f.readline()
      if shebang.startswith(b"#!"):
        if b"python" in shebang and not b"python2" in shebang:
          return True
    return False

  @classmethod
  def find_all(cls) -> list[Self]:
    return [
      cls(filename)
      for filename in sorted(os.listdir(ROOT))
      if "." not in filename and not os.path.isdir(os.path.join(ROOT, filename))
    ]

  @classmethod
  def find_no_main(cls) -> list[Self]:
    result = []

    for script in cls.find_all():
      if not script.is_python3():
        continue
      with open(script.path, "rb") as f:
        if not re.search(rb"^def main\(argv", f.read(), re.MULTILINE):
          result += [script]

    return result


class MainWrapper:
  real_main: ScriptProtocol.MainProtocol

  def __init__(self, filename: str):
    self.filename = filename

  def __call__(self, argv: list[str] | None = None, *args, **kwargs) -> int:
    result = self.real_main(self.fix_argv(argv, self.filename), *args, **kwargs)
    return result if isinstance(result, int) else 0

  @staticmethod
  def fix_argv(argv: list[str] | tuple[str, ...] | None, filename: str) -> list[str]:
    if not isinstance(argv, (list, tuple)) or len(argv) == 0:
      argv = [""]
    else:
      argv = list(argv[:])

    if not argv[0] or not isinstance(argv[0], str):
      argv[0] = filename

    return argv


class PythonMainWrapper(MainWrapper):
  def __init__(self, filename: str, real_main: ScriptProtocol.MainProtocol):
    self.filename = filename
    self.real_main = real_main


class ShellMainWrapper(MainWrapper):
  def __init__(self, filename: str):
    super().__init__(filename)

  def real_main(self, argv: list[str], *args, **kwargs) -> int:
    return self.Popen(argv).wait()

  def Popen(self, argv: list[str], *popen_args, **popen_kwargs) -> subprocess.Popen:
    popen_kwargs = popen_kwargs.copy()
    popen_kwargs["executable"] = self.filename
    return subprocess.Popen(argv, *popen_args, **popen_kwargs)


def main(argv: list[str]) -> int:
  prog = os.path.basename(argv[0])
  prog = prog if prog != "__main__.py" else __package__ or __name__

  if len(argv) < 2:
    print(f"Usage: {prog} {{script [args]|--no-main}}", file=sys.stderr)
    return 2

  if argv[1] == "--no-main":
    for script in Script.find_no_main():
      print(script.name)
    return 0

  return Script(argv[1]).load().main(argv[1:])


if __name__ == "__main__":
  try:
    sys.exit(main(sys.argv))
  except KeyboardInterrupt:
    pass
