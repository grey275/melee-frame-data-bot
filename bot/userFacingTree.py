import json

import discord

import config
import logs

import nodeStrategies

logger = logs.my_logger.getChild(__file__)


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
        self.name = name
        child_aliases = UserFacingNode._getChildAliases(node)
        buildChildren = strats.BuildChildren(UserFacingNode).buildChildren
        children = buildChildren(node['children'])
        valid_matches = ([*children.keys()]
                         + [*child_aliases.keys()])

        # Methods
        matchChild = strats.MatchChild(self.name, children,
                                       child_aliases, valid_matches).match
        handleArgs = strats.HandleArgs(matchChild).handleArgs
        handleNoArgs = strats.HandleNoArgs(node['output']).handleNoArgs

        self.respond = self.Respond(handleArgs, handleNoArgs).respond

    def _getChildAliases(node):
        aliases = dict()
        for name, child in node['children'].items():
            aliases.update({a: name for a in child['aliases']})
        return aliases

    class Respond:
        """
        Defines the main flow of control for queries to a node.
        """
        def __init__(self, handleArgs, handleNoArgs):
            self._handleArgs = handleArgs
            self._handleNoArgs = handleNoArgs

        def respond(self, user_args, **kwargs):
            if user_args:
                response = self._handleArgs(user_args, **kwargs)
            else:
                response = self._handleNoArgs(**kwargs)
            return response


def load(tree_loc=config.TREE_PATH):
    with open(tree_loc, 'r') as f:
        root_node = json.loads(f.read())
    return UserFacingNode("Root", root_node, nodeStrategies.Basic)


if __name__ == '__main__':
    tree = load()
