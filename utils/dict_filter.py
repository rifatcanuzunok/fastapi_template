def filter_none_values_func(pair):
    key, value = pair
    if value is None:
        return False
    else:
        return True


def filter_none_values(d: dict):
    return dict(filter(filter_none_values_func, d.items()))
