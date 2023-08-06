from dataclasses import is_dataclass


def dataclass_to_py(obj: object) -> str:
    """Exports a dataclass as python code."""
    if not is_dataclass(obj):
        raise TypeError("Only valid for dataclasses.")
    s = "from dataclasses import dataclass\n"
    for value in obj.__dict__.values():
        value_type = type(value)
        if value_type.__module__ != "builtins":
            s += f"from {value_type.__module__} import {value_type.__name__}\n"

    s += "\n\n@dataclass\n"
    s += f"class {type(obj).__name__}:\n"
    for key, value in obj.__dict__.items():
        if type(value).__name__ != "NoneType":
            s += f"    {key}: {type(value).__name__} = {value!r}\n"
        else:
            s += f"    {key} = {value}\n"

    return s
