import json

import discord

from .. import logs
from .. import config
from .. import messages
from .basic import Basic

logger = logs.my_logger.getChild(__file__)


class _BuildChildren(Basic.BuildChildren):
    def _defineChildStrats(self):
        self._special_child_strats = dict()
        self._default_child_strats = SuggestAlias


class _HandleArgs(Basic.HandleArgs):
    def handleArgs(self, user_args, msg_obj, *,
                   suggestion=None, path=None, **kwargs):
        if suggestion is None:
            try:
                user_args, suggestion = self._parseSuggestion(user_args)
            except ValueError:
                re = Basic.Response(messages.WrittenMSG('InvalidSuggestion'))
                return re.execResponse
            path = []  # no suggestion implies no path
        guess, *user_args = user_args
        match = self._matchChild(guess)
        matched_child, match, rate, is_aliased = match
        if rate < self.conf.min_match_percent:
            error = self._buildNotFoundMSG(guess, self._name,
                                           match, rate, is_aliased)
            return Basic.Response(error, msg_obj).execResponse
        else:
            path.append(match)
            return matched_child.respond(user_args, msg_obj,
                                         suggestion=suggestion,
                                         path=path)

    def _parseSuggestion(self, user_args):
        checks = [user_args.count('=') == 1, user_args[0]
                  is not '=', user_args[-1] is not '=']
        if not all(checks):
            raise ValueError('ur value is shit m8')
        seperator = user_args.index('=')
        target = user_args[:seperator]
        suggestion = user_args[seperator+1:]
        return target, suggestion


class _HandleNoArgs(Basic.HandleNoArgs):
    def __init__(self, raw_output, node_name, *,
                 child_names, **kwargs):
        self._args_required_msg = messages.WrittenMSG(
            "RequiresArg",
            name=node_name,
            valid_args=child_names).get()
        self._node_name = node_name
        self._child_names = child_names

    def handleNoArgs(self, msg_obj, path=None,
                     suggestion=None, **kwargs):
        if not path:
            return Basic.Response(self._args_required_msg,
                                  msg_obj).execResponse
        else:
            raw_output = messages.WrittenMSG('SuggestionReceived',
                                             path=path,
                                             suggestion=suggestion).get()
            output = self._buildOutput(raw_output)
            return _Response(output, msg_obj,
                             suggestion=suggestion,
                             path=path).execResponse


class _Response(Basic.Response):
    _conf = config.Suggest.Response

    def __init__(self, output, msg_obj, *, suggestion, path):
        self._channel = msg_obj.channel
        self._output = output
        self._path = path
        self._suggestion = suggestion

    async def execResponse(self):
        await self._queueSuggestion(self._suggestion, self._path)
        await self._send(self._output, self._channel)

    async def _queueSuggestion(self, suggestion, path):
        with open(self._conf.suggestion_que_loc, 'r+') as readQueue:
            breakpoint()
            raw = readQueue.read()
            print(f'raw: {raw}')
            if not raw:
                parsed = []
            else:
                parsed = json.loads(raw)
            print(f'parsed: {parsed}')
        with open(self._conf.suggestion_que_loc, 'w') as writeQueue:
            entry = {'sugg': suggestion, 'path': path}
            logger.debug(f'entry: {entry}')
            parsed.append(entry)
            json.dump(parsed, writeQueue)


class SuggestAlias:
    BuildChildren = _BuildChildren
    HandleNoArgs = _HandleNoArgs
    HandleArgs = _HandleArgs
    Response = _Response
    MatchChild = Basic.MatchChild
