from typing import cast, Dict, Optional

from . import api

# takes string or class instance
def extract_typed_id(obj) -> Dict[str, str]:  # { "type": "type", "id": "id" }
    if type(obj) is str:
        return {"type": "String", "id": obj}
    if not hasattr(obj, "__dict__"):
        raise TypeError(
            f"Expected a string or an instance of a class but received: {obj}"
        )
    if not hasattr(obj, "id"):
        raise TypeError(f"Expected {obj} to have an 'id' attribute")
    return {"type": obj.__class__.__name__, "id": str(obj.id)}


# takes string or
def extract_arg_query(
    obj,
) -> Dict[str, Optional[str]]:  # { "type": "type" | None, "id": "id" | None }
    if obj is None:
        return {"type": None, "id": None}
    if isinstance(obj, type):
        return {"type": obj.__name__, "id": None}
    try:
        return cast(Dict[str, Optional[str]], extract_typed_id(obj))
    except TypeError:
        raise TypeError(
            f"Expected None, a string, a class, or an instance of a class, but received: {obj}"
        )
