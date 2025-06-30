def ensure_set(a) -> set[str]:
    """ensure that the argument is convereted into a set but does not split a string
    Args:
        a: str | list[str] | set[str] | None

    Returns:
        set of strings
        'abc' -> {'abc', }
    """

    if a is None:
        return set()

    if isinstance(a, str):
        return {
            a,
        }

    else:
        return set(a)


def get_missing_fields(data: dict, missing_value) -> list:
    """Get the sub-dict that contains missing values"""
    return [field for field, value in data.items() if value == missing_value]


def key_list_to_dict(keys: list, missing_value):
    """Populate a dictionary with the given keys and fill with the missing value"""
    return dict.fromkeys(ensure_set(keys), missing_value)
