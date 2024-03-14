import sys

import __init__


def main(argv):
  return __init__.main(argv)

if __name__ == "__main__":
  try:
    sys.exit(main(sys.argv))
  except KeyboardInterrupt:
    pass
