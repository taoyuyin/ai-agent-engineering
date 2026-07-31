from typing import Any, Dict


TYPE_MAP = {"string": str, "integer": int, "number": (int, float), "boolean": bool}


def validate_arguments(arguments: Dict[str, Any], schema: Dict[str, Any]) -> None:
    if schema.get("type") != "object":
        raise ValueError("only object schemas are supported by this MVP")
    properties = schema.get("properties", {})
    missing = [name for name in schema.get("required", []) if name not in arguments]
    if missing:
        raise ValueError("missing required fields: " + ", ".join(missing))
    if schema.get("additionalProperties") is False:
        extras = set(arguments) - set(properties)
        if extras:
            raise ValueError("unexpected fields: " + ", ".join(sorted(extras)))

    for name, value in arguments.items():
        rule = properties.get(name)
        if rule is None:
            continue
        expected = TYPE_MAP.get(rule.get("type"))
        if expected and (not isinstance(value, expected) or isinstance(value, bool) and rule["type"] != "boolean"):
            raise ValueError("{} has invalid type".format(name))
        if "enum" in rule and value not in rule["enum"]:
            raise ValueError("{} is not an allowed value".format(name))
        if "minimum" in rule and value < rule["minimum"]:
            raise ValueError("{} is below minimum".format(name))
        if "maximum" in rule and value > rule["maximum"]:
            raise ValueError("{} exceeds maximum".format(name))
