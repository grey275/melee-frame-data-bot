class Suggest(DefaultRespondStrat):

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

    class SuggestNoArgs(DefaultNoArgStrat):
        def __init__(self, output):
            self._output = output

        def handleNoArgs(self, msg_obj, options, suggestion):
            self._queueSuggestion(suggestion)
            return self._output

        def _queueSuggestion(self, suggestion):
            with open(self.conf.suggestion_que_loc, 'w+r') as f:
                parsed = json.load(f)
                entry = {'sugg': suggestion, 'path': self._node_path}
                parsed.append(entry)
                json.dump(parsed, f)
