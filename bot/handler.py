"""
Handles commands sent by the user and executes the appropriate response.
"""
from . import config
from . import serviceAccount
from . import userFacingTree
from . import logs

logger = logs.my_logger.getChild(__file__)

conf = config.Handler


class ActiveTree:
    """
    For loading and reloading the user facing tree.
    This is currently the only object in the program
    which has directly modifiable state. The rest is
    IO operations.
    """
    session = serviceAccount.createSession()

    def __init__(self):
        self._tree = self._loadTree()
        self.respond = self._tree.respond

    def _loadTree(self):
        return userFacingTree.load()

    def reload(self):
        self._tree = self.loadTree()


_active_tree = ActiveTree()


async def handle(msg_obj):
    """
    Entry point for the main function of this module.
    """
    execResponse = await _query(msg_obj)
    await execResponse()


async def _query(msg_obj):
    """
    note: perhaps this shouldn't be separate from handle."""
    user_args, options = _parse(msg_obj.content)
    execResponse = _active_tree.respond(user_args, msg_obj=msg_obj,
                                        options=options)
    return execResponse


def _parse(content):
    """
    Parses command string into arguments which are used to search
    through the datastructure and options (words prefixed with a -)
    to pass to the response that's returned. The command prefix
    as well as the dash(-) delimiter on options are dropped.
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
