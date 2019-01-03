import yaml

from . import config
from . import logs


_logger = logs.my_logger.getChild(__file__)


class WrittenMSG:
    """
    Handwritten messages for the user. TODO The
    interface for this class is somewhat awkward. The
    class generally Might be better implemented as a
    function.
    """
    config = config.WrittenMSG

    def _fetchRawMsgs(message_file):
        with open(message_file, 'r') as f:
            msg_dict = yaml.load(f.read())
        return msg_dict

    _raw_msgs = _fetchRawMsgs(config.message_file)
    names = _raw_msgs.keys()

    def __init__(self, key, **info):
        """
        Instantiation produces a message accessible
        by the 'get' interface method.
        """
        msg = self._raw_msgs[key]
        self._info = info
        assert msg is not None
        if info:
            self._msg = self._format(msg)
        else:
            self._msg = msg

    def get(self):
        """ interface"""
        return [self._msg]

    def _format(self, msg):
        """
        Calls format(self._info) on all strings with self._info
        in potentially nested list, dict or str. Contains indirect
        recursion and so is somewhat slow, but it'll work for now.
        """
        if isinstance(msg, str):
            return self._formatText(msg)
        elif isinstance(msg, list):
            return self._formatList(msg)
        elif isinstance(msg, dict):
            return self._formatDict(msg)
        else:
            raise TypeError("Invalid type:{}".format(type(msg)))

    def _formatDict(self, dct):
        """
        Applies format(**info) to all strings in a dict.
        Embed objects can be constructed from a dict.
        """
        for key, val in dct.items():
            if val is None:
                raise ValueError("val is none")
            dct[key] = self._format(val)
        return dct

    def _formatList(self, lst):
        return [self._format(txt) for txt in lst]

    def _formatText(self, txt):
        return txt.format(**self._info)
