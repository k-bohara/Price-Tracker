import re


def get_float(value):
    if isinstance(value, (float, int)):
        return float(value)

    if isinstance(value, str):
        return float(re.sub('[^\d\.]', '', value))


def get_float_or_zero(value):
    try:
        return get_float(value)
    except:
        return 0.0


def get_float_or_none(value):
    try:
        return get_float(value)
    except:
        return None


def get_int(value):
    return int(get_float(value))


def get_int_or_zero(value):
    try:
        return get_int(value)
    except:
        return 0


def get_int_or_none(value):
    try:
        return get_int(value)
    except:
        return None
