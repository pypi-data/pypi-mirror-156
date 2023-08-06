# internal
from laz.utils.logging import get_logger
from laz.cli.parser import parser
from laz.utils.load import load
from laz.model.tree import Node
from laz.utils.iterator import Iterator


subparsers = parser.add_subparsers(required=True)

parser_init = subparsers.add_parser('tree')


def tree():
    args = parser.parse_args()
    get_logger(verbosity=args.verbose)
    root = load()
    print(root.configuration.name)
    for child in Iterator(root.children):
        _tree(child.value, '', child.is_last)


def _tree(node: Node, prefix: str = '', last: bool = False):
    symbol = '└─' if last else '├─'
    print(f'{prefix}{symbol} {node.configuration.name}')

    for child in Iterator(node.children):
        _tree(child.value, prefix + '│  ', child.is_last)
