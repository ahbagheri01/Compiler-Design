"""
created by Amirhossein Bagheri - 98105621 -> ahbagheri01@gmail.com
       &   Mohammad Jafari     - 98105654 -> mamad.jafari91@gmail.com
"""


def is_it_symbol(c: int) -> bool:
    """Gets a character unicode and determines if it is a symbol

    :param c: The input character Unicode code value
    :type c: int
    :return: a boolean representing whether c is a symbol or not
    :rtype: bool
    """
    return (40 <= c <= 45) or (58 <= c <= 61) or (c == 91) or c == 93 or c == 123 or c == 125


def is_it_unique_symbol(c: int) -> bool:
    """Gets a character unicode and determines if it is a unique symbol

    :param c: The input character Unicode code value
    :type c: int
    :return: a boolean representing whether c is a unique symbol or not
    :rtype: bool
    """
    return (c != 42) and ((40 <= c <= 45) or (58 <= c <= 60) or (c == 91) or c == 93 or c == 123 or c == 125)


def is_it_white_space(c: int) -> bool:
    """Gets a character unicode and determines if it is a white space

    :param c: The input character Unicode code value
    :type c: int
    :return: a boolean representing whether c is a white space or not
    :rtype: bool
    """
    return (9 <= c <= 13) or (c == 32)


def is_it_digit(c: int) -> bool:
    """Gets a character unicode and determines if it is a digit

    :param c: The input character Unicode code value
    :type c: int
    :return: a boolean representing whether c is a digit([0-9]) or not
    :rtype: bool
    """
    return 48 <= c <= 57


def is_it_valid(c: int) -> bool:
    """Gets a character unicode and determines if it is valid

    :param c: The input character Unicode code value
    :type c: int
    :return: a boolean representing whether c is valid or not
    :rtype: bool
    """
    return (97 <= c <= 122) or (65 <= c <= 90) or (47 <= c <= 57) or ((40 <= c <= 45) or (58 <= c <= 61) or (c == 91) or c == 93 or c == 123 or c == 125) or ((9 <= c <= 13) or (c == 32))


def is_it_letter(c: int) -> bool:
    """Gets a character unicode and determines if it is a letter([a-z,A-Z])

    :param c: The input character Unicode code value
    :type c: int
    :return: a boolean representing whether c is [a-z,A-Z] or not
    :rtype: bool
    """
    return (97 <= c <= 122) or (65 <= c <= 90)


def is_it_IDorNum_others(c: int) -> bool:
    """Gets a character unicode and determines if it is a id or number

    :param c: The input character Unicode code value
    :type c: int
    :return: return whether c is (id or number) or neither
    :rtype: bool
    """
    return is_it_white_space(c) or is_it_symbol(c) or c == 47
