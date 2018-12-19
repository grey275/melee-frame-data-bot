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

class UFN:
    """
    s
    """
    def __init__(self, BuildOutputStrat, BuildChildrenStrat, respondStrat):
        self._
    


    def __init__(self, )

class UserFacingNode:
    """
    Node on a tree containing an output and fuzzy
    searchable child nodes. if no 'user_args' are supplied
    to the respond() method, the _output_ is returned
    along with a set of behaviour modifiers to be
    interpreted by the Handler instance object which
    called respond()
    """
    _special_child_nodes = dict()

    conf = config.UserFacingNode
    _default_behaviours = Behaviours(send_dm=False, re_load=False)

    def __init__(self, name, node):
        """
        options holds other Response objects, and
        output holds any actual content to be displayed.
        """
        self._default_child_node = UserFacingNode
        self.name = name
        self._output = self._buildOutput(node['output'])
        self._child_aliases = self._getChildAliases(node)

        self._children = self._buildChildren(node)
        self._valid_matches = ([*self._children.keys()]
                               + [*self._child_aliases.keys()])

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

    def _getChildAliases(self, node):
        aliases = dict()
        for name, child in node['children'].items():
            aliases.update({a: name for a in child['aliases']})
        return aliases

    def _buildChildren(self, node):
        children = dict()
        for k, v in node['children'].items():
            if k in self._special_child_nodes:
                children[k] = self._special_child_nodes[k](k, v)
            else:
                children[k] = self._default_child_node(k, v)
        return children

    def respond(self, msg_obj, user_args, **kwargs):
        if user_args:
            response = self._handleArgs(msg_obj, user_args,
                                        **kwargs)
        else:
            response = self._handleNoArgs(msg_obj, **kwargs)
        return self._packageBehaviour(response)

    def _packageBehaviour(self, response):
        """
        checks to see if a behaviour has already been specified in the response
        and if not adds the default behaviour specified in the class
        """
        if isinstance(response, tuple):
            if not isinstance(response[1], Behaviours):
                raise TypeError(f'{response[1]} needs to be Behaviours')
            return response
        else:
            return response, self._default_behaviours

    def _handleArgs(self, msg_obj, user_args, **kwargs):
        guess, *user_args = user_args
        matched_child, match, rate, is_aliased = self._matchChild(msg_obj,
                                                                  guess)
        logger.debug(f'name: {self.name}, guess: {guess, }, match: {match}, ')
        if rate < self.conf.min_match_percent:
            error = self._buildNotFoundMSG(guess, self.name,
                                           match, rate, is_aliased)
            return error
        return matched_child.respond(msg_obj, user_args, **kwargs)

    def _buildNotFoundMSG(self, guess, category, match, rate, is_aliased):
        if is_aliased:
            match = f'{match} (alias for {self._child_aliases[match]})'
        msg = WrittenMSG('MatchNotFound',
                         guess=guess,
                         category=category,
                         closest_match=match,
                         match_rate=rate)
        return [msg.get()]

    def _matchChild(self, msg_obj, guess):
        """
        Searches for a child based on a guess supplied by the user.
        """
        match, rate = process.extractOne(guess, self._valid_matches)
        if match in self._child_aliases.keys():
            is_aliased = True
            matched_child = self._children[self._child_aliases[match]]
        else:
            is_aliased = False
            matched_child = self._children[match]
        return matched_child, match, rate, is_aliased

    def _handleNoArgs(self, msg_obj, options=None, **kwargs):
        if not self._output:
            error = WrittenMSG("RequiresArg",
                               name=self.name,
                               valid_args=self._children.keys()).get()
            return [error]
        behaviours = self._checkBehaviors(options)
        return (self._output, behaviours) if behaviours else self._output

    def _checkBehaviors(self, options):
        """
        here to allow subclasses to conditionally change behaviors
        """
        pass


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
