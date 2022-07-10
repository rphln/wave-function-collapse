def cursor(x, y):
    return f"\033[{y + 1};{x + 1}H"


def color(color):
    return f"\033[7;{color}m"


def reset():
    """
    The reset escape sequence.
    """

    return "\033[0m"


def clear():
    return "\033[2J"
