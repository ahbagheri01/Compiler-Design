import Scanner
import anytree
# from  Any_tree import anytree as anytree
import parser_utils.Transition_diagram as TD
from anytree import Node, RenderTree
from enum import Enum
from code_gen import code_generator as codGN

EPSILON = None


class ErrorTypes(Enum):
    ILLEGAL = 1
    MISSING = 2
    UNEXPECTED_EOF = 3


class ParseToken:
    def __init__(self):
        self.type = None
        self.value = ""
        self.code_value = ""

    def set_info(self, token):
        # print(token)
        token = token.split(",")
        self.type = token[0][1:]
        self.value = token[1][1:len(token[1]) - 1]
        if self.type == "KEYWORD" or self.type == "SYMBOL":
            self.code_value = token[1][1:len(token[1]) - 1]
        elif self.type == "NUM" or self.type == "ID":
            self.code_value = self.type
        if len(token) == 3:
            self.code_value = ','
            self.value = ','
        """
        self.grammar = json.load(open("./parser_utils/grammer.json"))
        self.first = json.load(open("./parser_utils/files/first.json"))
        self.follow = json.load(open("./parser_utils/files/follow.json"))
        self.predict = json.load(open("./parser_utils/files/predict.json"))
        """


class Parser:

    def __init__(self, path, save_path):
        self.save_path = save_path
        self.transition_diagram = TD.Diagram("./parser_utils/grammer.json", "./parser_utils/files/first.json",
                                             "./parser_utils/files/follow.json", "./parser_utils/files/predict.json")
        self.diagrams = self.transition_diagram.diagrams
        self.first = self.transition_diagram.first
        self.follow = self.transition_diagram.follow
        self.predict = self.transition_diagram.predict
        self.NT = self.transition_diagram.non_terminals
        self.T = self.transition_diagram.terminals
        self.stateN = self.transition_diagram.state_number
        self.scanner = Scanner.Scanner(path, save_path)
        self.stack = []
        self.push(self.diagrams[self.NT[0]])
        self.current_token = self.scanner.get_next_token()
        self.cur_state = self.front()
        self.p_token = ParseToken()
        self.p_token.set_info(self.current_token)
        self.root = Node(self.cur_state.main_grammar)
        self.current_node = self.root
        self.synchronous_set = self.follow
        self.line_number = 1
        self.errors = []
        self.is_stable = True
        self.code_generator = codGN.CodeGenerator(self, self.scanner)
        self.semantic_errors = self.code_generator.semantic.semantic_analyzer
        self.last_token = ""

    def front(self) -> TD.State:
        return self.stack[len(self.stack) - 1]

    def pop(self) -> TD.State:
        return self.stack.pop()

    def push(self, node: TD.State):
        self.stack.append(node)

    def get_next_token(self):
        # if self.scanner.get_line_number() == 3:
        # print("here")
        self.last_token = self.current_token
        self.current_token = self.scanner.get_next_token()
        if self.current_token != "$":
            self.p_token.set_info(self.current_token)
        else:
            self.p_token.code_value = "$"

    def is_all_terminal(self, states):
        for state in states:
            if state not in self.T:
                return False
        return True

    def print_stack(self):
        for i in self.stack:
            if str(i) == "24":
                print(end="")
            print(i, end=" ")
        print("")

    def handle_epsilons(self, state, node):
        if 'null' in state.states.keys():
            Node('epsilon', node)
            return

        for production in state.states.keys():
            if production in self.NT:
                a = Node(self.diagrams[production].main_grammar, node)
                self.handle_epsilons(self.diagrams[production], a)
                next_state = state.states[production]
                while next_state.stateType != TD.StateType.ACC:
                    for next_node in next_state.states.keys():
                        b = Node(next_node, node)
                        self.handle_epsilons(self.diagrams[next_node], b)
                        next_state = next_state.states[next_node]

    def code_gen(self, action):
        if self.scanner.get_line_number() == 47 and action == "#repeat_jump":
            print("here")
        if action == "#save_break":
            print("here")
        print(f'line = {self.scanner.get_line_number()}')
        if (action == "#push_type" or
                action == "#push_op" or action == "#push_id" or action == "#push_num" or action == "#push_num_temp"):  # or  # action == "#decl_id"):
            self.code_generator.generate_code(action, self.last_token)
        else:
            self.code_generator.generate_code(action, self.current_token)

    def parse(self):
        action_flag = False
        while True:
            while self.cur_state.stateType != TD.StateType.ACC:
                next_states_list = list(self.cur_state.states.keys())
                for production in self.cur_state.states.keys():
                    if production[0] == "#":
                        action_flag = True
                        self.code_gen(production)
                        self.cur_state = self.cur_state.states.get(production)
                        break
                    if production in self.T:
                        if production == self.p_token.code_value:
                            temp = self.cur_state.states.get(self.p_token.code_value)
                            Node(f'({self.p_token.type}, {self.p_token.value})' if production != '$' else '$',
                                 parent=self.current_node)
                            self.cur_state = temp
                            self.get_next_token()
                            break
                        if self.p_token.code_value in next_states_list and self.cur_state.stateType == TD.StateType.MID:
                            temp = self.cur_state.states.get(self.p_token.code_value)
                            Node(f'({self.p_token.type}, {self.p_token.value})' if production != '$' else '$',
                                 parent=self.current_node)
                            self.cur_state = temp
                            self.get_next_token()
                            break
                        if self.cur_state.stateType == TD.StateType.START:
                            continue
                        temp = self.cur_state.states.get(production)
                        self.cur_state = temp
                        if production != self.p_token.code_value:
                            if self.current_token == "$":
                                self.errors.append(
                                    [ErrorTypes.UNEXPECTED_EOF, self.scanner.get_line_number() + 1, None])
                                self.write_to_file()
                                return
                            self.is_stable = False
                            line_number = self.scanner.get_line_number()
                            self.errors.append([ErrorTypes.MISSING, line_number, production])
                            if production == "$":
                                self.write_to_file()
                                return
                        break
                    else:
                        if self.p_token.code_value in self.first[production]:
                            self.current_node = Node(self.diagrams[production].main_grammar, parent=self.current_node)
                            self.push(self.cur_state.states[production])
                            self.push(self.diagrams[production])
                            self.cur_state = self.front()
                            break
                        elif EPSILON in self.first[production] and self.p_token.code_value in self.follow[production]:
                            a = Node(self.diagrams[production].main_grammar, parent=self.current_node)
                            self.cur_state = self.cur_state.states[production]
                            self.handle_epsilons(self.diagrams[production], a)
                            break
                else:
                    line_number = self.scanner.get_line_number()
                    if EPSILON in self.first[production] and self.p_token.code_value in self.follow[production]:
                        self.cur_state = self.cur_state.states[production]
                        self.current_node = self.current_node.parent
                    elif self.cur_state.stateType != TD.StateType.START and self.p_token.code_value in self.follow[
                        production]:
                        if self.current_token == "$":
                            self.errors.append([ErrorTypes.UNEXPECTED_EOF, self.scanner.get_line_number() + 1, None])
                            self.write_to_file()
                            return
                        self.errors.append([ErrorTypes.MISSING, line_number, production])
                        self.cur_state = self.cur_state.states[production]
                        self.is_stable = False
                    elif not (self.p_token.code_value in self.synchronous_set[self.cur_state.main_grammar]):
                        if self.current_token == "$":
                            self.errors.append([ErrorTypes.UNEXPECTED_EOF, self.scanner.get_line_number() + 1, None])
                            self.write_to_file()
                            return
                        self.errors.append([ErrorTypes.ILLEGAL, line_number, self.p_token.code_value])
                        self.get_next_token()
                        self.is_stable = False
                    else:
                        if self.current_token == "$":
                            self.errors.append([ErrorTypes.UNEXPECTED_EOF, self.scanner.get_line_number() + 1, None])
                            self.write_to_file()
                            return
                        self.errors.append([ErrorTypes.MISSING, line_number, self.cur_state.main_grammar])
                        self.pop()
                        self.cur_state = self.pop()
                        self.is_stable = False
            if action_flag:
                action_flag = False
                continue
            if len(self.stack) < 2:
                break

            self.is_stable = True
            self.pop()
            self.cur_state = self.pop()
            self.current_node = self.current_node.parent

        if self.stack[0].number == 0 and self.current_token == "$":
            print("parsed well")

        if not self.is_stable:
            self.errors.append([ErrorTypes.UNEXPECTED_EOF, self.scanner.get_line_number() + 1, None])

        self.write_to_file()

    def print_tree(self):
        tree = ''
        for pre, fill, node in RenderTree(self.root):
            tree += "%s%s\n" % (pre, node.name)
        print(tree)

    def write_to_file(self, address='/parse_tree.txt', syntax_errors_address='/syntax_errors.txt'):
        tree = ''
        for pre, fill, node in RenderTree(self.root):
            tree += "%s%s\n" % (pre, node.name)

        code_gen = ''
        semantic_errors = ''
        if len(self.semantic_errors.semantic_errors) == 0:
            semantic_errors = 'The input program is semantically correct.'
        else:
            for error in self.semantic_errors.semantic_errors:
                semantic_errors += error + '\n'

        if len(self.semantic_errors.semantic_errors) != 0:
            code_gen = 'The output code has not been generated.'
        else:
            for i, val in enumerate(self.code_generator.program_block):
                try:
                    op, y, z, x = val
                    code_gen += "%d\t(%s, %s, %s, %s)\n" % (i, op, y, '' if z is None else z, '' if x is None else x)
                except:
                    op, y, z, x, dec = val
                    code_gen += "%d\t(%s, %s, %s, %s)\n" % (i, op, y, '' if z is None else z, '' if x is None else x)

        syntax_errors = ''
        if len(self.errors) == 0:
            syntax_errors = 'There is no syntax error.'
        else:
            for error_type, line, error in self.errors:
                if error_type == ErrorTypes.ILLEGAL:
                    syntax_errors += f'#{line} : syntax error, illegal {error}\n'
                elif error_type == ErrorTypes.MISSING:
                    syntax_errors += f'#{line} : syntax error, missing {error}\n'
                elif error_type == ErrorTypes.UNEXPECTED_EOF:
                    syntax_errors += f'#{line} : syntax error, Unexpected EOF\n'

        with open(self.save_path + address, "w", encoding="utf-8") as opened_file:
            opened_file.write(tree)
        opened_file.close()

        with open(self.save_path + syntax_errors_address, "w", encoding="utf-8") as opened_file:
            opened_file.write(syntax_errors)
        opened_file.close()

        with open(self.save_path + '/output.txt', "w", encoding="utf-8") as opened_file:
            opened_file.write(code_gen)

        with open(self.save_path + '/semantic_errors.txt', "w", encoding="utf-8") as opened_file:
            opened_file.write(semantic_errors)

        opened_file.close()
