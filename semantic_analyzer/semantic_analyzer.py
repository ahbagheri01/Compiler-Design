from scope_records import scope_record as sr
import Scanner


class SemanticAnalyzer:
    def __init__(self, scanner):
        self.semantic_stack = []
        self.semantic_errors = []
        self.error_handler = []
        self.scanner = scanner
        self.functions_argument = {'output':('output', 'void', 1, [('int', 'a')])}
        self.function_to_call = ''

    def pop(self):
        return self.semantic_stack.pop()

    def push(self, val):
        self.semantic_stack.append(val)

    def front(self):
        return self.semantic_stack[len(self.semantic_stack) - 1]

    def scoping_error(self, ID):
        line = self.scanner.get_line_number()
        self.semantic_errors.append(f'#{line} : Semantic Error! \'{ID}\' is not defined.')

    def void_type_error(self, ID):
        line = self.scanner.get_line_number() - 1
        self.semantic_errors.append(f'#{line} : Semantic Error! Illegal type of void for \'{ID}\'.')

    def break_statement_error(self):
        line = self.scanner.get_line_number()
        self.semantic_errors.append(f'#{line} : Semantic Error! No \'repeat ... until\' found for \'break\'.')

    def type_mismatch_error(self, expected, real):
        line = self.scanner.get_line_number()
        self.semantic_errors.append(
            f'#{line} : Semantic Error! Type mismatch in operands, Got {real} instead of {expected}.')

    def parameter_matching_error(self, index, lexeme, expected, real):
        line = self.scanner.get_line_number()
        self.semantic_errors.append(
            f'#{line} : Semantic Error! Mismatch in type of argument {index} of \'{lexeme}\'. Expected \'{expected}\' but got \'{real}\' instead.')

    def parameter_count_matching_error(self, ID):
        line = self.scanner.get_line_number()
        self.semantic_errors.append(f'#{line} : Semantic Error! Mismatch in numbers of arguments of \'{ID}\'.')

    def handle_argument_errors(self):
        print('DICK')
        last_call = self.find_last_call()
        func_info = self.functions_argument[self.function_to_call]
        number_of_args = func_info[2]
        # print(number_of_args, len(self.error_handler) - last_call - 1, ',,,')
        if (len(self.error_handler) - last_call - 2) != number_of_args:
            self.parameter_count_matching_error(func_info[0])
        number_of_args = min(len(self.error_handler) - last_call - 2, number_of_args)
        for i in range(number_of_args):
            expected_type, lexeme = func_info[3][i]
            current_type = self.error_handler[last_call + i + 1][1]
            print(expected_type, current_type, '+++++++++++++++')
            if expected_type != current_type:
                self.parameter_matching_error(i+1, self.function_to_call, expected_type, current_type)

        for i in range(len(self.error_handler) - last_call):
            self.error_handler.pop()

        print(self.error_handler)

    def update_function_args(self, function, id, type):
        if function != '':
            print(self.functions_argument, function)
            self.functions_argument[function][-2] += 1  # increase arguments
            self.functions_argument[function][-1].append((type, id))  # add to params-list

    def find_last_call(self):
        for i in range(len(self.error_handler)-1, -1, -1):
            if self.error_handler[i] == 'call':
                return i
        return None

