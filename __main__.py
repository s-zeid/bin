import sys

from . import main


if __name__ == "__main__":
  try:
    sys.exit(main(sys.argv))
  except KeyboardInterrupt:
    pass
