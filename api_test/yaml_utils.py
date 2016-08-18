

def get_reference(node, identifiers):
    """Recurses through yaml node to find the target key."""
    if len(identifiers) == 1:
        return {identifiers[0]: node[identifiers[0]]}

    if not identifiers[0]:  # skip over any empties
        return get_reference(node, identifiers[1:])
    return get_reference(node[identifiers[0]], identifiers[1:])


def traverse_yaml(node, function, **kwargs):
    """General function for traversing a dictionary representation of yaml.

        node -- root of yaml dictionary to traverse
        function -- function to be called for all non-structural (dict/list) yaml nodes
        kwargs -- additional arguments to pass into the function
    """
    if not isinstance(node, dict):
        return
    # Changed from iteritems() to items() because if we use iteritems() then when we receive a
    # reference item. So when we update the node item we run into a runtime error because the
    # size of the dictionary changes. However, using items() it returns a copy of the node so
    # modifications wont trigger a run time error.
    for key, item in node.items():
        function(node, key, item, **kwargs)
        if isinstance(item, dict):
            traverse_yaml(item, function, **kwargs)

        elif isinstance(item, list):
            for sub_item in item:
                if isinstance(sub_item, dict):
                    traverse_yaml(sub_item, function, **kwargs)
