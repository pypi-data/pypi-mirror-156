import re
from typing import Any
from typing import Dict


def parse_nested_key(hub, key_to_parse: str):
    """
    Parse key to resolve the data in the new_state. Format like 0['virtual_cloud']['subnetwork'] is resolved to
    ['0', 'virtual_cloud', 'subnetwork'] using regular expression. Use single quotes to capture dictionary keys.
    """
    keys = re.findall(r"\[([^\[\]]*)\]", key_to_parse)

    stripped_keys = [str.strip(key, "'") for key in keys]
    nested_keys = [key_to_parse[0 : key_to_parse.index("[")]]
    if keys:
        for index in stripped_keys:
            nested_keys.append(index)

    return nested_keys


def data_lookup(hub, state_data: Dict[Any, Any], attribute_path: str):
    """
    Lookup the new_state data referenced by arg_binding template using the attribute path.
    For example '0[hosted_zone][name]' will resolve the value for new_state[0][hosted_zone][name] if it exists
    """

    nested_keys = parse_nested_key(hub, key_to_parse=attribute_path)
    if nested_keys:
        for key in nested_keys:
            numeric_key = None
            if key.isnumeric():
                numeric_key = int(key)

            if key in state_data:
                state_data = state_data[key]
            elif numeric_key is not None and numeric_key in state_data:
                state_data = state_data[numeric_key]
            else:
                hub.log.debug(f"Could not find `{attribute_path}` in new_state.")
                break

    return state_data


async def find_arg_reference_data(hub, arg_bind_expr: str):
    """
    Resolve ${cloud:state:attribute_path} expressions to a value used in jinja using the hub's RUNNING dictionary
    """

    state_data = None

    run_name = hub.idem.RUN_NAME

    arg_bind_arr = arg_bind_expr.split(":")

    if len(arg_bind_arr) < 2:
        hub.log.debug(
            f" arg-bind expression `{arg_bind_expr}` doesn't comply with standards. Expected format is "
            f"$'{'resource_state:resource_name:attribute-path'}'  "
        )
        return state_data, False

    state_id = arg_bind_arr[1]

    attribute_path = None

    if len(arg_bind_arr) > 2:
        attribute_path = arg_bind_arr[2]

    run_data = hub.idem.RUNS.get(run_name, None)
    low_data = None
    if run_data:
        low_data = run_data.get("low", None)

    tag = None
    if low_data:
        for low in low_data:
            if "__id__" in low and low["__id__"] == state_id:
                ctx = low.get("ctx", None)
                if ctx:
                    tag = ctx.get("tag", None)
                break

    arg_bind_template = "${" + arg_bind_expr[0] + "}"

    if not tag:
        hub.log.debug(
            f"Could not parse `{arg_bind_expr}` in jinja. The data for arg_binding reference `{arg_bind_template}` "
            f"could not be found on the hub. "
        )
        return state_data, False

    if run_data:
        executed_states = run_data.get("running", None)
        if executed_states is not None and tag in executed_states:
            state_data = executed_states.get(tag).get("new_state", None)
            if state_data and attribute_path:
                state_data = data_lookup(hub, state_data, attribute_path)

    return state_data, True
