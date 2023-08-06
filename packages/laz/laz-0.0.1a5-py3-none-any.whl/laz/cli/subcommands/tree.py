# internal
from laz.utils.logging import get_logger
from laz.cli.parser import parser
from laz.utils.load import load
from laz.model.tree import Node
from laz.utils.iterator import Iterator
from laz.utils.node import get_node_configuration


subparsers = parser.add_subparsers(required=True)

parser_tree = subparsers.add_parser('tree')
parser_tree.add_argument('--show-targets', '-t', action='store_true', default=False, help='Show targets.')


def tree():
    args = parser.parse_args()
    get_logger(verbosity=args.verbose)
    root = load()
    print(f'{root.configuration.name} {_targets(root, args.show_targets)}')
    for child in Iterator(root.children):
        _tree(child.value, '', child.is_last, args.show_targets)


def _tree(node: Node, prefix: str = '', last: bool = False, show_targets: bool = False):
    symbol = '└─' if last else '├─'
    print(f'{prefix}{symbol} {node.configuration.name} {_targets(node, show_targets)}')

    for child in Iterator(node.children):
        _tree(child.value, prefix + '│  ', child.is_last, show_targets)


def _targets(node: Node, show_targets: bool = False) -> str:
    if show_targets:
        configuration = get_node_configuration(node)
        if len(configuration.target_names) > 0:
            names = ', '.join(configuration.target_names)
            return f'({names})'
    return ''
