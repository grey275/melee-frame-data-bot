import json
import sheets
import serviceAccount
from searchableTree import SearchableTree


def buildDataTree(node):
    tree = dict()
    tree['aliases'] = list()
    if isinstance(node, SearchableTree):
        tree["children"] = {n.name: buildDataTree(n) for n in node._children.values()}
    return tree


session = serviceAccount.createSession()
data = sheets.AllStructuredData(session)

tree = {n.name: buildDataTree(n) for n in data._children.values()}

with open("tree.json", "w") as f:
    f.write(json.dumps(tree))
