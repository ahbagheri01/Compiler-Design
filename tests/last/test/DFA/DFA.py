from enum import Enum
from .CharHandler import *

"""
created by Amirhossein Bagheri - 98105621 -> ahbagheri01@gmail.com
       &   Mohammad Jafari     - 98105654 -> mamad.jafari91@gmail.com
"""


class Node:
    def __init__(self, node_name, is_it_final=False, is_it_error=False, error_type=None,
                 lookahead=False, token_type=None, token_matter=False):
        """
            initialize the Node
        """
        self.node_name = node_name
        self.is_it_final = is_it_final
        self.is_it_error = is_it_error
        self.error_type = error_type
        self.lookahead = lookahead
        self.token_type = token_type
        self.token_matter = token_matter

from enum import Enum
class Token(Enum):
    id = "ID"
    keyword = "KEYWORD"
    num = "NUM"
    symbol = "SYMBOL"
    comment = "COMMENT"
    white_space = "WHITESPACE"


class Error(Enum):
    invalid_input = "Invalid input"
    invalid_number = "Invalid number"
    unmatched_comment = "Unmatched comment"
    unclosed_comment = "Unclosed comment"


class DFA:
    def __init__(self, load_mode=False, save_mode=False, load_path="dfa.txt", save_path="dfa.txt"):
        """
        initialize the DFA module
        """

        self.states = {-2: Node(node_name=-2, is_it_final=True, is_it_error=True, error_type=Error.invalid_input, lookahead=True),
                        -1: Node(node_name=-1, is_it_final=True, is_it_error=True, error_type=Error.invalid_input),
                        0: Node(node_name=0),
                        1: Node(node_name=1),
                        2: Node(node_name=2, is_it_final=True, is_it_error=True, error_type=Error.invalid_number),
                        3: Node(node_name=3, is_it_final=True, lookahead=True, token_type=Token.num, token_matter=True),
                        4: Node(node_name=4),
                        5: Node(node_name=5, is_it_final=True, lookahead=True, token_type=Token.id, token_matter=True),
                        6: Node(node_name=6, is_it_final=True, token_type=Token.symbol, token_matter=True),
                        7: Node(node_name=7),
                        8: Node(node_name=8, is_it_final=True, lookahead=True, token_type=Token.symbol, token_matter=True),
                        9: Node(node_name=9, is_it_final=True, token_type=Token.symbol, token_matter=True),
                       10: Node(node_name=10),
                       11: Node(node_name=11, is_it_final=True, lookahead=True, token_type=Token.white_space),
                       12: Node(node_name=12),
                       13: Node(node_name=13, is_it_final=True, is_it_error=True, error_type=Error.unmatched_comment),
                       14: Node(node_name=14, is_it_final=True, lookahead=True, token_type=Token.symbol, token_matter=True),
                       15: Node(node_name=15),
                       16: Node(node_name=16),
                       17: Node(node_name=17, is_it_final=True, token_type=Token.comment),
                       18: Node(node_name=18),
                       19: Node(node_name=19),
                    }

        try:
            if load_mode:
                self.table = self.load_table(load_path)
            else:
                self.table = self.initialize_table()
            if save_mode:
                self.save_dfa(save_path)
        except:
            pass

    def get_state(self, current_state: int, c: int) -> Node:
        """Gets the next state we have to go

        :param current_state: The state we're currently in
        :param c: The character input
        :return: Returns a node representing the node we should go to
        """
        return self.states.get(self.table[current_state][c])

    def initialize_table(self) -> list:
        """[summary]
            Returns:
                list: 2D list of all transitions and state
            """
        table = [[(-2 if is_it_valid(i) else -1) for i in range(256)] for j in range(20)]

        """ initialization of table """
        for i in range(256):
            if is_it_digit(i):
                self.__digit_dfa_handler(table, i)
            else:
                table[1][i] = 2
            if is_it_letter(i):
                self.__letter_dfa_handler(table, i)

            if is_it_white_space(i):
                self.__white_space_dfa_handler(table, i)
            else:
                table[10][i] = 11

            if is_it_unique_symbol(i):
                self.__unique_symbol_dfa_handler(table, i)
            elif i == 61:  # is input is =
                self.__equal_sign_dfa_handler(table)
            if is_it_valid(i) and i!= 61:
                table[7][i] = 8  # remark the others of symbol table

            if i == 47:  # if input is /
                self.__slash_sign_dfa_handler(table)
            elif is_it_valid(i):
                table[12][i] = 14

            if i == 42:  # if input is *
                self.__star_sign_dfa_handler(table)
            else:
                table[18][i] = 18  # remark the others of comment for state 12
                if i != 47:  # input is not /
                    table[19][i] = 18  # remark others of comment for state 13

            if is_it_IDorNum_others(i):
                self.__id_and_number_dfa_handler(table, i)

            if i == 10:  # if input is line feed
                table[16][i] = 17
            else:
                table[16][i] = 16

        return table

    @staticmethod
    def __digit_dfa_handler(table, i):
        """Arranges Actions for the case that input character is a digit([0-9])

        :param table: The table we want to modify
        :param i: The input digit character Unicode code
        """
        table[0][i] = 1
        table[1][i] = 1
        table[4][i] = 4

    @staticmethod
    def __letter_dfa_handler(table, i):
        """Arranges Actions for the case that input character is a letter([a-z,A-Z])

        :param table: The table we want to modify
        :param i: The input letter character Unicode code
        """
        table[0][i] = 4
        table[4][i] = 4
        table[1][i] = 2

    @staticmethod
    def __white_space_dfa_handler(table, i):
        """Arranges Actions for the case that input character is a white space

        :param table: The table we want to modify
        :param i: The input white space character Unicode code
        """
        table[0][i] = 10
        table[10][i] = 10

    @staticmethod
    def __unique_symbol_dfa_handler(table, i):
        """Arranges Actions for the case that input character is a unique symbol

        :param table: The table we want to modify
        :param i: The input unique symbol character Unicode code
        """
        table[0][i] = 6

    @staticmethod
    def __equal_sign_dfa_handler(table):
        """Arranges Actions for the case that input character is =

        :param table: The table we want to modify
        """
        table[0][61] = 7
        table[7][61] = 9

    @staticmethod
    def __slash_sign_dfa_handler(table):
        """Arranges Actions for the case that input character is a /

        :param table: The table we want to modify
        """
        table[0][47] = 15
        table[12][47] = 13
        table[15][47] = 16
        table[19][47] = 17

    @staticmethod
    def __star_sign_dfa_handler(table):
        """Arranges Actions for the case that input character is *

        :param table: The table we want to modify
        """
        table[0][42] = 12
        table[15][42] = 18
        table[18][42] = 19
        table[19][42] = 19

    @staticmethod
    def __id_and_number_dfa_handler(table, i):
        """Arranges Actions for the case that input character is a id or number

        :param table: The table we want to modify
        :param i: The input character Unicode code
        """
        table[1][i] = 3
        table[4][i] = 5

    def save_dfa(self, path: str):
        """Saves the dfa in txt file

        :param path: get path to save file as txt
        :return:
        """
        wr = ""
        for i in range(len(self.table)):
            for j in range(len(self.table[0])):
                wr += f"{self.table[i][j]} "
            wr += "\n"
        with open(path, "w") as opened_file:
            opened_file.write(wr)

    def load_table(self, path: str) -> list:
        """Loads the dfa from a txt file

        :param path: get input txt file path
        :return: return the 2D array of DFA
        """
        self.table = []
        with open(path, "r") as opened_file:
            for line in opened_file:
                line.replace('\n', ' ')
                temp = list(map(int, line.split()))
                self.table.append(temp)

        return self.table




