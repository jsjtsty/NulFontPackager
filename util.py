def get_value_or_default(dictionary: dict, key, default):
    if key in dictionary:
        return dictionary[key]
    else:
        return default


def get_value_or_except(dictionary: dict, key, error: Exception):
    if key in dictionary:
        return dictionary[key]
    else:
        raise error
