"""
A set of strategies to be passed when instantiating UserFacingNode.
"""
from fuzzywuzzy import process

import messages
import logs
import config


logger = logs.my_logger.getChild(__file__)


class Interface:
    """
    This interface isn't actually inherited anywhere;
    it's here for documentation purposes.
    """
    class BuildChildren:
        def __init__(self, default_child_type, special_children: dict):
            self._default_child_type = default_child_type
            self._special_children = special_children

        def buildChildren(node_children):
            """
            Defines how children should be built based on this node's children.
            """
            pass

    class HandleArgs:
        """
        called when args are passed to a node's response method
        """
        def __init__(matchChild, valid_matches):
            pass

        def handleArgs(self):
            pass

    class HandleNoArgs:
        """
        Called when no args are passed to the node's response method
        """
        def __init__(output, node_name, valid_matches):
            pass

        def handleArgs(self):
            pass

        pass

    class MatchChild:
        """
        Used by HandleArgs to resolve attempts to find a child.
        """
        def __init__(self, children, child_aliases, valid_matches):
            pass

        def match():
            pass

    class AsyncBehaviour:
        """
        Contains an async method to be passed back to the handler
        and added to the event loop, as well as potentially context
        for its execution.
        """
        def __init__(self):
            pass

        async def execute():
            pass


class Basic:
    """
    The strategy for most of the nodes in the network.
    No special behaviours.
    """

    class BuildChildren:

        def __init__(self, UserFacingNode):
            self._default_child_type = Basic
            self._special_child_types = dict()
            self._UserFacingNode = UserFacingNode

        def buildChildren(self, node_children):
            """
            Defines how children should be built based on this raw node's children.
            """
            children = dict()
            for child_name, child_node in node_children.items():
                if child_name in self._special_child_types:
                    strat = self._special_child_types[child_name]
                else:
                    strat = self._default_child_type
                children[child_name] = self._UserFacingNode(child_name,
                                                            child_node, strat)
            return children

    class HandleNoArgs:
        def __init__(self, output, node_name, valid_matches):
            self._output = output
            self._requires_arg = messages.WrittenMSG("RequiresArg",
                                                     name=node_name,
                                                     valid_args=valid_matches)

        def handleNoArgs(self, options, **kwargs):
            if not self._output:
                return self._requires_arg.get()
            return self._output

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
            return [msg.get()]

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

    class AsyncBehaviour:
        def __init__(self):
            pass

        async def execute():
            pass

    class Respond:
        """
        Defines the main flow of control for queries to a node.
        """
        def __init__(self, handleArgs, handleNoArgs, packageAsyncBehaviour):
            self._handleArgs = handleArgs
            self._handleNoArgs = handleNoArgs
            self._packageAsyncBehaviour = packageAsyncBehaviour

        def respond(self, user_args, **kwargs):
            if user_args:
                response = self._handleArgs(user_args, **kwargs)
            else:
                response = self._handleNoArgs(**kwargs)
            return self._packageAsyncBehaviour(response)

    class PackageAsyncBehaviour:
        def __init__(self, asyncBehaviour):
            self._asyncBehaviour = asyncBehaviour

        def package(self, response):
            """
            checks to see if a behaviour has already been included in the
            response and if not adds the behaviour passed to the instance
            object's constructor
            """
            if isinstance(response, tuple):
                return response
            else:
                return response, self._asyncBehaviour
