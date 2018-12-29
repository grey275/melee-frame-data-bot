import json

import discord

from . import config
from . import logs

from . import nodeStrategies

_logger = logs.my_logger.getChild(__file__)


class UserFacingNode:
    """
    Node which can be queried for information according to user arguments.
    Typical behaviour is either searching child nodes based on a given argument
    or simply returning this node's output, potentially packaged with some
    async behaviour to be run by the handler(for example, to refresh the tree
    if some new element was added, or additional messages for discord.)
    """
    def __init__(self, name, node, strats):
        """
        Context for self.respond is determined here by
        a series of dependency injections, utilizing the
        methods passed in with strats"""
        # Values
        child_aliases = UserFacingNode._getChildAliases(node)
        buildChildren = strats.BuildChildren(UserFacingNode).buildChildren
        children = buildChildren(node)
        has_children = bool(children)
        child_names = [*children.keys()]
        alias_names = [*child_aliases.keys()]
        valid_matches = child_names + alias_names

        # Methods
        matchChild = strats.MatchChild(name, children, child_aliases,
                                       valid_matches).match
        handleArgs = strats.HandleArgs(
            name, matchChild, has_children).handleArgs
        handleNoArgs = strats.HandleNoArgs(
            node['output'],
            node_name=name,
            child_names=child_names,
            Response=strats.Response
        ).handleNoArgs
        self.name = name
        self.respond = UserFacingNode.Respond(handleArgs, handleNoArgs).respond

    def _getChildAliases(node):
        aliases = dict()
        for name, child in node['children'].items():
            aliases.update({a: name for a in child['aliases']})
        return aliases

    class Respond:
        """
        main control flow for control for queries to a node.
        """
        def __init__(self, handleArgs, handleNoArgs):
            self._handleArgs = handleArgs
            self._handleNoArgs = handleNoArgs

        def respond(self, user_args, msg_obj, **kwargs):
            if user_args:
                response = self._handleArgs(user_args, msg_obj, **kwargs)
            else:
                response = self._handleNoArgs(msg_obj, **kwargs)
            return response


def load(tree_loc=config.TREE_PATH):
    with open(tree_loc, 'r') as f:
        root_node = json.loads(f.read())
    return UserFacingNode("Root", root_node, nodeStrategies.Root)


def findEmbeds(node, name):
    if isinstance(node, dict):
        for k, v in node.items():
            findEmbeds(v, name)
    elif isinstance(node, list):
        for e in node:
            findEmbeds(e, name)
    elif isinstance(node, discord.Embed):
        print(f'embed found in {name}')
    elif isinstance(node, str):
        print(f'str in {name}')
    else:
        raise ValueError(f'idk why this is here: {node}')


if __name__ == '__main__':
    tree = load()
