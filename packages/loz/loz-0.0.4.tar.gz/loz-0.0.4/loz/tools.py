"""
helper functions
"""
import logging
import random
import string

logger = logging.getLogger("loz")


class color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def multiline_input(text):
    print(text)
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line:
            break
        contents.append(line)
    return "\n".join(contents)


def make_password(length):
    selectable_punctuation = "+-=_&?/\\%#@~,."
    chars = (
        string.ascii_lowercase
        + string.ascii_uppercase
        + string.digits
        + selectable_punctuation
    )
    password = "".join(random.choice(chars) for x in range(length))
    return password
