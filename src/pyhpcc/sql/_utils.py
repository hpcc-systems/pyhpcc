def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]
