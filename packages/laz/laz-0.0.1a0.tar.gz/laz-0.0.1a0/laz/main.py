# std
import sys

# internal
from laz.utils import log


def main():
    log.debug(sys.argv[1:])
    if len(sys.argv) == 2 and (sys.argv[1] == 'version' or sys.argv[1] == '--version'):
        from laz.cli.subcommands.version import version
        version()
    else:
        from laz.cli.root import root
        root()


if __name__ == '__main__':
    cmd = 'laz version'
    sys.argv = cmd.split(' ')
    main()
