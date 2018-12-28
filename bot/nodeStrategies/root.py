"""
For the root node.
"""

from .basic import Basic
from .dminstead import DMInstead
from .suggestAlias import SuggestAlias


class _BuildChildren(Basic.BuildChildren):

    def _defineChildStrats(self):

        self._default_child_strats = Basic
        self._special_child_strats = {
            "Help": DMInstead,
            "Info": DMInstead
        }

    def buildChildren(self, node):
        children = super().buildChildren(node)
        children["SuggestAlias"] = self._UserFacingNode(
            'SuggestAlias', node, SuggestAlias
        )
        return children


class Root(Basic):
    BuildChildren = _BuildChildren
