"""
created by Amirhossein Bagheri - 98105621 -> ahbagheri01@gmail.com
       &   Mohammad Jafari     - 98105654 -> mamad.jafari91@gmail.com
"""
import Scanner
import Parser
"""
for i in range(10,20):
    read_path = "./parser_T11-T20/T%2d" % (i+1)
    save_path = "./parser_T11-T20/T%2d" % (i+1)
    scanner = Scanner.Scanner(path=save_path, save_path=save_path)
    parser = Parser.Parser(read_path, save_path)
    parser.parse()
"""
read_path = "./"
save_path = "./"
scanner = Scanner.Scanner(path=save_path, save_path=save_path)
parser = Parser.Parser(read_path, save_path)
parser.parse()
