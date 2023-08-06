# std
from typing import List

# internal
from laz.model.tree import Node
from laz.model.path import Path
from laz.model.resolver import Resolver
from laz.model.target import Target
from laz.model.act import Act


class Runner:

    def __init__(self, root_node: Node, args: List[str]):
        self.root_node = root_node
        self.path = Path(args[0])
        self.args = args[1:]

    def resolve(self) -> List[Target]:
        resolver = Resolver(self.root_node, self.path)
        return resolver.resolve()

    def run(self):
        targets = self.resolve()
        for target in targets:
            act = Act(target, self.args)
            act.act()
