def schema_errors(record: dict, schema: dict) -> list[str]:
    errors = []
    for field, (kind, required) in schema.items():
        value = record.get(field)
        if value is None and required:
            errors.append(f"missing {field}")
        elif value is not None and not isinstance(value, kind) or isinstance(value, bool) and kind is int:
            errors.append(f"bad {field}")
    return errors


if __name__ == "__main__":
    schema = {"id": (int, True), "name": (str, True)}
    schema["age"] = (int, False)
    errors = schema_errors({"id": True, "age": "x"}, schema)
    assert errors == ["bad id", "missing name", "bad age"]
    assert schema_errors({"id": 1, "name": "a"}, schema) == []
