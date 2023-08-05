import inspect
from typing import Dict
from typing import List


def ignore_parameter_changes(
    hub,
    ignore_changes: List,
    params: Dict,
    param_signatures: Dict[str, inspect.Parameter],
):
    """
    Set an optional parameter within params to None according to the parameter path in ignore_changes. For example,
    path key1:key2 path will result to {key1: {key2: None}}
    :param ignore_changes: A list of path of parameters that will be assigned to None value
                           to ignore being updated in present().
    :param params: A dict of parameter-value pairs.
    :param param_signatures: A dict containing the parameter signatures.
    """
    for param_path in ignore_changes:
        # Split the path with ":"
        path = param_path.split(":")
        if path[0] in ["hub", "ctx", "name"]:
            continue
        # We can only assigning None to the optional parameters which default is not inspect._empty
        if (
            path[0] in param_signatures
            and param_signatures.get(path[0]).default != inspect._empty
        ):
            _nullify_parameter(path=path, params=params)


def _nullify_parameter(path: str, params: Dict):
    """
    Go through a dictionary according to the path and replace the destination value with None.
    For example, if path is a:b, params {"a": {"b": "value"}} will become {"a": {"b": None}}
    """
    if len(path) > 1 and path[0] in params:
        _nullify_parameter(path[1:], params[path[0]])
    elif len(path) == 1 and path[0] in params:
        params[path[0]] = None
    else:
        return
