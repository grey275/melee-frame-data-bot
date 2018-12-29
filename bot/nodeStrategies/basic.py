"""
The strategy for most of the nodes in the network.
No special behaviours.
"""
import discord
from fuzzywuzzy import process

from .. import logs
from .. import messages
from .. import config
_logger = logs.my_logger.getChild(__file__)


class _BuildChildren:

    def __init__(self, UserFacingNode):
        self._defineChildStrats()
        self._UserFacingNode = UserFacingNode

    def _defineChildStrats(self):
        self._default_child_strats = Basic
        self._special_child_strats = dict()

    def buildChildren(self, node):
        """
        names found in the self._special_child_strats attribute
        will be given their special strategies, and other nodes
        will be given the basic strategy"""
        node_children = node['children']
        children = dict()
        for child_name, child_node in node_children.items():
            if child_name in self._special_child_strats:
                strats = self._special_child_strats[child_name]
            else:
                strats = self._default_child_strats
            children[child_name] = self._UserFacingNode(child_name,
                                                        child_node, strats)
        return children


class _HandleNoArgs:
    def __init__(self, raw_output, *, node_name, child_names, Response):
        self._node_name = node_name
        if not raw_output:
            self._output = messages.WrittenMSG(
                "RequiresArg",
                name=node_name,
                valid_args=child_names)
        else:
            self._output = self._buildOutput(raw_output)
        self._Response = Response

    def handleNoArgs(self, msg_obj, **kwargs):
        response = self._Response(self._output, msg_obj, **kwargs)
        return response.execResponse

    def _buildOutput(self, raw_output):
        output = []
        for out in raw_output:
            if 'embed' in out:
                out['embed'] = self._makeEmbed(**out['embed'])
            output.append(out)
        return output

    def _makeEmbed(self, fields, **embed_info):
        embed = discord.Embed(**embed_info)
        for f in fields:
            embed.add_field(**f)
        return embed


class _Response:
    def __init__(self, output, msg_obj, **kwargs):
        self._output = output
        self._channel = msg_obj.channel

    async def execResponse(self):
        await self._send(self._output, self._channel)

    async def _send(self, output, channel):
        _logger.debug(f'sending {output}')
        for out in output:
            await channel.send(**out)


class _HandleArgs:
    conf = config.HandleArgs

    def __init__(self, name, matchChild, has_children):
        self._name = name
        self._matchChild = matchChild
        self._has_children = has_children

    def handleArgs(self, user_args, msg_obj, **kwargs):
        if not self._has_children:
            error = messages.WrittenMSG("NoArgTaken",
                                        name=self._name).get()
            return Basic.Response(error, msg_obj).execResponse
        guess, *user_args = user_args
        (matched_child, match,
            rate, is_aliased) = self._matchChild(guess)
        if rate < self.conf.min_match_percent:
            error = self._buildNotFoundMSG(guess, self._name,
                                           match, rate, is_aliased)
            return Basic.Response(error, msg_obj).execResponse
        else:
            return matched_child.respond(user_args, msg_obj, **kwargs)

    def _buildNotFoundMSG(self, guess, category, match, rate, is_aliased):
        if is_aliased:
            match = f'{match} (alias for {self._child_aliases[match]})'
        msg = messages.WrittenMSG('MatchNotFound',
                                  guess=guess,
                                  category=category,
                                  closest_match=match,
                                  match_rate=rate)
        return msg.get()


class _MatchChild:
    def __init__(self, node_name, children, child_aliases, valid_matches):
        self._node_name = node_name
        self._children = children
        self._child_aliases = child_aliases
        self._valid_matches = valid_matches

    def match(self, guess):
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
        _logger.debug(f'category: {self._node_name}, '
                      f'guess: {guess, }, '
                      f'match: {match},')
        return matched_child, match, rate, is_aliased


class Basic:
    BuildChildren = _BuildChildren
    HandleNoArgs = _HandleNoArgs
    HandleArgs = _HandleArgs
    MatchChild = _MatchChild
    Response = _Response
