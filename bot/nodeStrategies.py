import messages
import logs

from fuzzywuzzy import process

logger = logs.my_logger.getChild(__name__)


class Interface:
    class IBuildChildren:
        def __init__(self, default_child_type, special_children: dict):
            self._default_child_type = default_child_type
            self._special_children = special_children

        def buildChildren(node_children):
            """
            Defines how children should be built based on this node's children.
            """
            pass

    class IHandleArgs:
        def __init__(matchChild, valid_matches):
            pass

        def handleArgs(self):
            pass

    class IHandleNoArgs:
        def __init__(output, node_name, valid_matches):
            pass

        def handleArgs(self):
            pass

        pass

    class IMatchChild:
        def __init__(self, children, child_aliases, valid_matches):
            pass

        def match():
            pass
        pass

    class IAsyncBehaviour:
        async def execute():
            pass


class Basic:

    class BuildChildren:

        def __init__(self, UserFacingNode):
            self._default_child_type = Basic
            self._special_child_types = dict()
            self._UserFacingNode = UserFacingNode

        def buildChildren(self, node_children):
            """
            Defines how children should be built based on this node's children.
            """
            children = dict()
            for child_name, child_node in node_children:
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
        def __init__(self, matchChild):
            self._matchChild = matchChild

        def handleArgs(self, msg_obj, user_args, **kwargs):
            guess, *user_args = user_args
            matched_child, match, rate, is_aliased = self.match(msg_obj, guess)
            logger.debug(f'name: {self.name}, '
                         f'guess: {guess, }, match: {match},')
            if rate < self.conf.min_match_percent:
                error = self._buildNotFoundMSG(guess, self.name,
                                               match, rate, is_aliased)
                return error
            elif user_args:
                return matched_child.handleArgs(user_args, **kwargs)
            else:
                return matched_child.respond(**kwargs)

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
        def __init__(self, children, child_aliases, valid_matches):
            self._children = children
            self._child_aliases = child_aliases
            self._valid_matches = valid_matches

        def match(self, msg_obj, guess):
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

    class AsyncBehaviour:
        def __init__(self):
            pass

        def execute():
            pass

    class Respond:
        """
        Defines the main flow of control for queries to a node.
        """
        def __init__(self, handleArgs, handleNoArgs, packageBehaviour):
            self._handleArgs = handleArgs
            self._handleNoArgs = handleNoArgs
            self._packageBehaviour = packageBehaviour

        def respond(self, user_args, **kwargs):
            pass

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
