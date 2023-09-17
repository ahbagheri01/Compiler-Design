from enum import Enum
import DFA.DFA
from DFA import *

"""
created by Amirhossein Bagheri - 98105621 -> ahbagheri01@gmail.com
       &   Mohammad Jafari     - 98105654 -> mamad.jafari91@gmail.com
"""


class SymbolTableItem:

    def __init__(self, token_type, name, id):
        """Initializes the symbol table item
        """
        self.token_type = token_type
        self.id = id
        self.name = name


class EOFERROR(Exception):
    pass


class Scanner:

    def __init__(self, path,save_path):
        """
        this function is called at the instantiation of module Scanner
        :arg
        path : the path of the file to be written and compiled by program
        path : the path of the file to be written and compiled by program
        """
        self.save_path = save_path
        self.input_address = path+'/input.txt'
        self.input_file = open(self.input_address, "r")
        self.symbol_address = save_path+"/symbol_table.txt"
        self.token_address = save_path+"/tokens.txt"
        self.error_address = save_path+"/lexical_errors.txt"
        self.line_number = 0
        self.char_index = 0
        self.current_state = 0
        self.current_lexeme = ""
        self.buffer = "not empty"
        self.buffer_size = 0
        self.DFA = DFA.DFA(load_mode=False, save_mode=False, save_path="dfa.txt")
        self.symbol_Table = SymbolTable()
        self.error_table = {}
        self.token_table = {}
        self.line_number_of_comment = 0
    def get_line_number(self):
        return self.line_number


    def get_next_token(self):
        """Handles the scan and whole process of making the tables if we reach the end of file"""
        token = self.get_next_token_scanner()
        if not token:
            if self.current_state == 18 or self.current_state == 19 or self.current_state == 15:
                if self.current_state !=15:
                    self.insert_error(line_number=self.line_number_of_comment, error_type=DFA.Error.unclosed_comment,error_lexeme=self.current_lexeme)
                else:
                    self.insert_error(line_number=self.line_number_of_comment,error_type=DFA.Error.invalid_input,error_lexeme=self.current_lexeme)
            if self.current_state == 1 or self.current_state == 4 or self.current_state == 7 or self.current_state == 12:
                next = self.current_state + 1
                if self.current_state == 12 or self.current_state == 1:
                    next += 1
                token = self.get_token_string(self.DFA.states[next],self.current_lexeme)
                self.insert_token(token=token, line_number=self.line_number)
            self.input_file.close()
            self.save_token()
            self.save_errors()
            self.symbol_Table.save_symbol_table(self.symbol_address)
            return "$"
        self.insert_token(token=token, line_number=self.line_number)
        return token

    def get_next_token_scanner(self):
        """Looks for the next Token in the line until it finds one

        :return: The found token
        """
        while self.buffer != "":
            while self.char_index < self.buffer_size:
                input_char = self.buffer[self.char_index]
                ascii_code = ord(input_char)
                next_state = self.DFA.get_state(self.current_state, ascii_code)
                if next_state.node_name == 15:
                    self.line_number_of_comment = self.line_number
                if next_state.is_it_final:
                    if next_state.token_matter:
                        if next_state.lookahead:
                            token = self.get_token_string(next_state, self.current_lexeme)
                        else:
                            self.char_index += 1
                            token = self.get_token_string(next_state, self.current_lexeme+input_char)
                        self.current_state = 0
                        self.current_lexeme = ""
                        return token
                    if next_state.is_it_error:
                        if next_state.lookahead:
                            self.insert_error(self.line_number, next_state.error_type, self.current_lexeme)
                        else:
                            self.insert_error(self.line_number, next_state.error_type,
                                              self.current_lexeme + str(input_char))
                    self.current_lexeme = ""
                    self.current_state = 0
                else:
                    self.current_lexeme += input_char
                    self.current_state = next_state.node_name
                self.char_index += 1
                if next_state.lookahead:
                    self.char_index -= 1
            self.read_next_line()
        return False

    def insert_error(self, line_number, error_type: DFA.Error, error_lexeme: str):
        """Inserts the error to error table

        :param line_number: The index of the line we're currently in
        :param error_type: The type of the error
        :param error_lexeme: The lexeme of the error
        """
        if error_type == DFA.Error.unclosed_comment:
            if len(error_lexeme) > 7:
                error_lexeme = f"{error_lexeme[0:7]}..."
            else:
                error_lexeme = f"{error_lexeme}..."
            error_lexeme = error_lexeme.replace("\n", "")
        temp = self.error_table.get(line_number, None)
        if temp is None:
            self.error_table[line_number] = f"({error_lexeme}, {error_type.value})"
        else:
            self.error_table[line_number] = f"{temp} ({error_lexeme}, {error_type.value})"

    def read_next_line(self):
        """Increments the line number to read the next line
        """
        self.buffer = self.input_file.readline()
        self.buffer_size = len(self.buffer)
        if self.buffer_size != 0:
            self.line_number += 1
        self.char_index = 0

    def get_token_string(self, state, lexeme):
        """ Generates the token string in the desired format

        :param state: The state we're currently in
        :param lexeme: The lexeme of the token
        :return: Returns the token in a desired format
        """
        if state.token_type == DFA.Token.id:
            id, type_of_token, lexeme = self.symbol_Table.get_token(lexeme)
            return f"({type_of_token.value}, {lexeme})"
        else:
            return f"({state.token_type.value}, {lexeme})"

    def insert_token(self, token: str, line_number) -> (int, DFA.Token, str):
        """ Inserts a token to token table

        :param token: The token we want to insert
        :param line_number: The index of the line we want to insert the token into
        """
        temp = self.token_table.get(line_number, None)
        if temp is None:
            self.token_table[line_number] = token
        else:
            self.token_table[line_number] = f"{temp} {token}"

    def save_token(self):
        """Writes the tokens into a file where is located on self.token_address
        """
        with open(self.token_address, "w") as opened_file:
            for (key, val) in self.token_table.items():
                opened_file.write(f"{key}.\t{val}\n")

    def save_errors(self):
        """Writes the errors into a file where is located on self.error_address
        """
        with open(self.error_address, "w") as opened_file:
            for (key, val) in self.error_table.items():
                opened_file.write(f"{key}.\t{val}\n")
            if len(self.error_table) == 0:
                opened_file.write("There is no lexical error.\n")


class SymbolTable:
    def __init__(self):
        """Initialize the symbol table
        """
        self.table = {"if": 1,
                      "else": 2,
                      "void": 3,
                      "int": 4,
                      "repeat": 5,
                      "break": 6,
                      "until": 7,
                      "return": 8,
                      "endif" : 9
                      }
        self.last_keyword = len(self.table)
        self.last_id = self.last_keyword+1

    def get_token(self, lexeme: str) -> (int, DFA.Token, str):
        """Gives the token id and its lexeme and adds it to the symbol table if doesn't already exists
        :param lexeme: The lexeme of the token
        :return: Returns the information we need about the token
        """
        temp = self.table.get(lexeme, None)
        if temp is None:
            self.table[lexeme] = self.last_id
            self.last_id += 1
            return self.last_id, DFA.Token.id, lexeme
        if temp <= self.last_keyword:
            return temp, DFA.Token.keyword, lexeme
        return temp, DFA.Token.id, lexeme

    def save_symbol_table(self, address):
        """Writes the symbol table into a file

        :param address: a path to save the symbol table on
        """
        with open(address, "w") as opened_file:
            for (key, val) in self.table.items():
                opened_file.write(f"{val}.\t{key}\n")
