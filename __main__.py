import sys

import __init__

if __name__ == "__main__":
 try:
  sys.exit(__init__.main(sys.argv))
 except KeyboardInterrupt:
  pass
