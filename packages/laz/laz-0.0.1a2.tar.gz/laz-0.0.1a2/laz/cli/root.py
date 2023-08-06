# std
import argparse
import sys
from typing import List, Tuple

# internal
from laz.utils.errors import LazRuntimeError
from laz.cli.parser import parser
from laz.utils.load import load
from laz.utils.logging import get_logger
from laz.model.runner import Runner


def root():
    cli_args, laz_args = _split_args()
    if len(laz_args) == 0:
        raise LazRuntimeError('No path provided')
    elif len(laz_args) == 1:
        raise LazRuntimeError('No arguments provided')
    cli_args = parser.parse_args(cli_args)
    get_logger(verbosity=cli_args.verbose)
    root_node = load()
    runner = Runner(root_node, laz_args)
    runner.run()


def _split_args() -> Tuple[List[str], List[str]]:
    for i, s in enumerate(sys.argv):
        if i > 0 and not s.startswith('-'):
            return sys.argv[1:i], sys.argv[i:]
    return sys.argv[1:], []
