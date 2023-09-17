import Scanner
import os

"""
created by Amirhossein Bagheri - 98105621 -> ahbagheri01@gmail.com
       &   Mohammad Jafari     - 98105654 -> mamad.jafari91@gmail.com
"""


def read_file(file_path):
    """Reads a file from a given path

    :param file_path: a path to the file 
    """
    with open(file_path, "r") as opened_file:
        return opened_file.readlines()


for i in range(10):
    cur_path = os.path.dirname(__file__)
    print(cur_path)
    path = os.path.relpath(f"{os.getcwd()}\\test\\test", cur_path)
    print(path)

    n = f"0{i + 1}" if i >= 9 else f"{i+1}"

    error = read_file(f"{path}\\T{n}\\lexical_errors.txt")
    token = read_file(f"{path}\\T{n}\\tokens.txt")
    symbol = read_file(f"{path}\\T{n}\\symbol_table.txt")
