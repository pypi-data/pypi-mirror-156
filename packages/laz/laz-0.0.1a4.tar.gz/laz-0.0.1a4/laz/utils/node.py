# std
import os

# internal
from laz.model.configuration import Configuration
from laz.model.tree import Node
from laz.model.target import Target


def get_target_configuration(node: Node, target_name: str) -> Target:
    target = Target(target_name)
    target.push({'target': {'name': target_name}})
    target.push(get_node_configuration(node).data)
    target.push(node.configuration.get_target(target_name).data)
    return target


def get_node_configuration(node: Node) -> Configuration:
    nodes = node.root_path()
    data = {
        'dirpath': os.path.dirname(node.configuration.filepath),
        'filepath': node.configuration.filepath,
        'name': node.configuration.name,
    }
    conf = Configuration(node.configuration.id, **data)
    for node in nodes:
        conf.push(node.configuration.data)
    return conf
