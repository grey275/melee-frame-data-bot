"""
A set of strategies to be passed when instantiating UserFacingNode.
"""
from fuzzywuzzy import process
import discord

import messages
import logs
import config


logger = logs.my_logger.getChild(__file__)


class Basic:
    """
    The strategy for most of the nodes in the network.
    No special behaviours.
    """

    class BuildChildren:

        def __init__(self, UserFacingNode):
            self._UserFacingNode = UserFacingNode
            self._defineChildStrategies()

        def _defineChildStrategies(self):
            """
            Defines how children should be built based on this
            raw node's children.
            """
            self._special_child_strats = dict()
            self._default_child_strats = Basic

        def buildChildren(self, node_children):
            """
            names found in the self._special_child_strats attribute
            will be given their special strategies, and other nodes
            will be given the basic strategy"""
            children = dict()
            for child_name, child_node in node_children.items():
                if child_name in self._special_child_strats:
                    strats = self._special_child_strats[child_name]
                else:
                    strats = self._default_child_strats
                children[child_name] = self._UserFacingNode(child_name,
                                                            child_node, strats)
            return children

    class HandleNoArgs:
        def __init__(self, raw_output):
            self._raw_output = raw_output

        def handleNoArgs(self, options, msg_obj, **kwargs):
            response = Basic.Response(self._raw_output,
                                      msg_obj, options, **kwargs)
            return response.execResponse

    class Response:
        def __init__(self, raw_output, msg_obj, options, **kwargs):
            self._output = self._buildOutput(raw_output)
            self._channel = msg_obj.channel

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

        async def execResponse(self):
            await self._send(self._output, self._channel)

        async def _send(self, output, channel):
            logger.debug(f'sending {output}')
            for out in output:
                await channel.send(**out)

    class HandleArgs:
        conf = config.HandleArgs

        def __init__(self, matchChild):
            self._matchChild = matchChild

        def handleArgs(self, user_args, **kwargs):
            guess, *user_args = user_args
            (matched_child, match,
             rate, is_aliased) = self._matchChild(guess)
            if rate < self.conf.min_match_percent:
                error = self._buildNotFoundMSG(guess, self.name,
                                               match, rate, is_aliased)
                return error
            else:
                return matched_child.respond(user_args, **kwargs)

        def _buildNotFoundMSG(self, guess, category, match, rate, is_aliased):
            if is_aliased:
                match = f'{match} (alias for {self._child_aliases[match]})'
            msg = messages.WrittenMSG('MatchNotFound',
                                      guess=guess,
                                      category=category,
                                      closest_match=match,
                                      match_rate=rate)
            return msg.get()

    class MatchChild:
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
            logger.debug(f'name: {self._node_name}, '
                         f'guess: {guess, }, '
                         f'match: {matched_child},')
            return matched_child, match, rate, is_aliased

# class DMInstead:
#     class Response(Basic.Response):
#         def __init__(self, output, msg_obj, **kwargs):
#             super().__init__(output, msg_obj, **kwargs)
#             self._notification = messages.WrittenMSG('DMNotify').get()

#         async def execute(self):
#             author = self._msg_obj.author.dm_channel
#             if not author.dm_channel:
#                 await author.create_dm()
#             await self._send(self._output,
#                              self._msg_obj.author.dm_channel)
#             await self._send()(self._notification,
#                                self._msg_obj.channel)

class Root:
    """
    For the root node.
    """
    class BuildChildren(Basic.BuildChildren):
        def _defineChildStrategies(self):
            self._special_child_strats = {'suggest': Suggest}
            self._default_child_strats = Basic

    class HandleNoArgs():
        pass
            # self._requires_arg = messages.WrittenMSG("RequiresArg",
            #                                          name=node_name,
            #                                          valid_args=valid_matches)

class Suggest:
    pass
