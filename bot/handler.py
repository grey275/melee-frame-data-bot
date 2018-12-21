import config
import serviceAccount
import userFacingTree
import logs

logger = logs.my_logger.getChild(__file__)

conf = config.Handler


class ActiveTree:
    """
    For loading and reloading the user facing tree.
    """
    session = serviceAccount.createSession()

    def __init__(self):
        self._tree = self.loadTree()
        self.respond = self._tree.respond

    def loadTree(self):
        return userFacingTree.load()

    def reload(self):
        self._tree = self.loadTree()


_active_tree = ActiveTree()


async def handle(msg_obj):
    """
    """
    execResponse = await _query(msg_obj)
    await execResponse()


async def _query(msg_obj):
    """ init should not be called directly. Instead use the
    query staticmethod"""
    user_args, options = _parse(msg_obj.content)
    execResponse = _active_tree.respond(user_args, msg_obj=msg_obj,
                                        options=options)
    return execResponse


def _parse(content):
    """
    Parses command string into arguments to search through
    the datastructure with, and options (words prefixed with a -)
    to pass to the response that's returned. The
    command prefix as well as the leading dash on options
    are dropped.
    """
    words = content[len(conf.command_prefix):].split()
    args = []
    options = []
    for w in words:
        if w[0] == '-':
            options.append(w[1:])
        else:
            args.append(w)
    return args, options
