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
        Using a strategy-like design pattern, much of the functionality
        is determined by the classes passed into __init__"""
        # Values
        self.name = name
        output = self._buildOutput(node['output'])
        child_aliases = self._getChildAliases(node)
        buildChildren = strats.BuildChildren(UserFacingNode).buildChildren
        children = buildChildren(node['children'])
        valid_matches = ([*children.keys()]
                         + [*child_aliases.keys()])

        # Functions
        matchChild = strats.MatchChild(children, child_aliases,
                                       valid_matches).match
        handleArgs = strats.HandleArgs(matchChild).handleArgs
        handleNoArgs = strats.HandleNoArgs(output, self.name,
                                           valid_matches).handleNoArgs
        asyncBehaviour = strats.AsyncBehaviour.execute
        package = strats.PackageAsyncBehaviour(asyncBehaviour).package

        self.respond = strats.Respond(handleArgs, handleNoArgs,
                                      package).respond

    def _getChildAliases(self, node):
        aliases = dict()
        for name, child in node['children'].items():
            aliases.update({a: name for a in child['aliases']})
        return aliases

    def _buildOutput(self, raw_output):
        output = raw_output
        for i, out in enumerate(output):
            if 'embed' in out:
                output[i]['embed'] = self._makeEmbed(**out['embed'])
        return output

    def _makeEmbed(self, fields, **embed_info):
        embed = discord.Embed(**embed_info)
        for f in fields:
            embed.add_field(**f)
        return embed


def load(tree_loc=config.TREE_PATH):
    with open(tree_loc, 'r') as f:
        root_node = json.loads(f.read())
    return UserFacingNode("Root", root_node, nodeStrategies.Basic)


if __name__ == '__main__':
    tree = load()
