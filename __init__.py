#!/usr/bin/env python

import imp
import os
import re
import subprocess
import sys
import types

ROOT = os.path.abspath(os.path.dirname(__file__))

class ShellScript(object):
 __slots__ = ["filename"]
 def __init__(self, filename):
  self.filename = filename
 def __call__(self, *argv):
  if len(argv) == 1 and isinstance(argv[0], (list, tuple)):
   argv = argv[0]
  return self.Popen(argv).wait()
 def Popen(self, argv, *popen_args, **popen_kwargs):
  argv = fix_argv(argv, self.filename)
  popen_kwargs = popen_kwargs.copy()
  popen_kwargs["executable"] = self.filename
  return subprocess.Popen(argv, *popen_args, **popen_kwargs)

class MainWrapper(object):
 __slots__ = ["filename", "original"]
 def __init__(self, original, filename):
  self.filename = filename
  self.original = original
 def __call__(self, argv=None, *args, **kwargs):
  self.original(fix_argv(argv, self.filename), *args, **kwargs)

def fix_argv(argv, filename):
 if not isinstance(argv, (list, tuple)) or len(argv) == 0:
  argv = [None]
 else:
  argv = list(unicode(i).encode("utf-8") if not isinstance(i, basestring) else i
              for i in argv[:])
 if not isinstance(argv[0], basestring) or not argv[0]:
  argv[0] = filename
 return argv

def script(script, name=None):
 if name == None:
  name = os.path.basename(script).replace("-", "_")
 script = os.path.join(ROOT, script)
 with open(script, "rb") as f:
  if "python" in f.xreadlines().next():
   is_python = True
  else:
   is_python = False
 if is_python:
  dont_write_bytecode = sys.dont_write_bytecode
  sys.dont_write_bytecode = True
  module = imp.load_source(name, script)
  sys.dont_write_bytecode = dont_write_bytecode
  module.__file__ = os.path.abspath(module.__file__)
  if callable(getattr(module, "main", None)):
   module.main = MainWrapper(module.main, module.__file__)
 else:
  module = types.ModuleType(name)
  module.__file__ = os.path.abspath(script)
  module.main = ShellScript(module.__file__)
  sys.modules[name] = module
 return module

def scripts():
 return [i for i in sorted(os.listdir(ROOT))
         if "." not in i and not os.path.isdir(os.path.join(ROOT, i))]

def no_main():
 r = []
 for i in scripts():
  with open(i, "rb") as f:
   if "python" not in f.xreadlines().next():
    continue
  with open(i, "rb") as f:
   if not re.search(r"^def main\(argv", f.read(), re.MULTILINE):
    r += [i]
 return r

def main(argv):
 if len(argv) < 2:
  print >> sys.stderr, "Usage: %s script [args]" % argv[0]
  return 2
 return script(argv[1]).main(argv[1:])
