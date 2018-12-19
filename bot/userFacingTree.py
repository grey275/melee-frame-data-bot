import json

from collections import namedtuple

import discord

from fuzzywuzzy import process

import config
import logs

from messages import WrittenMSG

logger = logs.my_logger.getChild(__name__)

# Behaviour tuples signal for the Handler object which called
# UserFacingNode.respond() to handle the response in a particular way or
# to do something in addition to displaying the output.
Behaviours = namedtuple('Behaviors', ['send_dm', 're_load'])


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
        handleArgs = strats.HandleArgs(matchChild, valid_matches).handleArgs
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


class Suggest(UserFacingNode):
    """
    Node for making suggestions.
    """
    conf = config.Suggest
    _default_behaviours = Behaviours(send_dm=False, re_load=True)
    _special_child_nodes = dict()
    _output = [WrittenMSG('SuggestionReceived').get()]

    def __init__(self, node_name, node, node_path=[]):
        self.name = f'{node_name} Suggest'
        self._node_path = node_path + [node_name]
        if node_name == 'all':
            Suggest._root_node = node
        self._default_child_node = Suggest
        self._children = self._buildChildren(node)
        self._child_aliases = self._getChildAliases(node)
        self._valid_matches = ([*self._children.keys()]
                               + [*self._child_aliases.keys()])

    def respond(self, msg_obj, user_args, options=None, suggestion=None):
        if not suggestion:
            target, suggestion = self._parseSuggestion(user_args)
        else:
            target = user_args
        return super().respond(msg_obj, target, options=options,
                               suggestion=suggestion)

    def _parseSuggestion(self, user_args):
        checks = [user_args.count('=') == 1, user_args[0]
                  is not '=', user_args[-1] is not '=']
        if not all(checks):
            raise ValueError('ur value is shit m8')
        seperator = user_args.index('=')
        target = user_args[:seperator]
        suggestion = user_args[seperator+1:]
        return target, suggestion

    def _handleNoArgs(self, msg_obj, options, suggestion):
        self._queueSuggestion(suggestion)
        return self._output

    def _queueSuggestion(self, suggestion):
        with open(self.conf.suggestion_que_loc, 'w+r') as f:
            parsed = json.load(f)
            entry = {'sugg': suggestion, 'path': self._node_path}
            parsed.append(entry)
            json.dump(parsed, f)


class LongOutput(UserFacingNode):
    '''
    User facing node which DMs the user except when
    supplied with the "nodm" keyword.
    '''
    _default_behaviours = Behaviours(send_dm=True, re_load=False)

    def _checkBehaviors(self, options):
        if 'nodm' in options:
            return Behaviours(send_dm=False, re_load=False)
        else:
            return self._default_behaviours


class Root(UserFacingNode):
    '''
    root node for the user facing tree.
    '''
    _default_child_node = UserFacingNode
    _special_child_nodes = {
        'Help': LongOutput,
        'Info': LongOutput,
        'Suggest': Suggest
    }

    def _buildChildren(self, node):
        children = dict()
        for k, v in node['children'].items():
            if k in self._special_child_nodes:
                children[k] = self._special_child_nodes[k](k, v)
            else:
                children[k] = self._default_child_node(k, v)

        children['Suggest'] = Suggest(self.name, node)
        return children

    def _buildSuggestNode(self):
        pass

    def __init__(self, node):
        super().__init__('all', node)


def load(tree_loc=config.TREE_LOC):
    with open(tree_loc, 'r') as f:
        root_node = json.loads(f.read())
    return Root(root_node)


if __name__ == '__main__':
    tree = load()
