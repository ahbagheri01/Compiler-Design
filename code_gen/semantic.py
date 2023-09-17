from semantic_analyzer import semantic_analyzer as sa
from code_gen.Memory_handler import Memory
from scope_records import scope_record as sr
from collections import namedtuple
import code_gen.Break_handler as bh

"""
# num
address
! ooffset
@ address
"""
from collections import namedtuple

Three_Address_Code = namedtuple('ThreeAddressCode', 'op y z x')
Three_Address_Code2 = namedtuple('ThreeAddressCode', 'op y z x dec')
ops = {'+': 'ADD', '-': 'SUB', '*': 'MULT', "<": "LT", "==": "EQ"}


class Semantic:
    def print_program_block(self):
        i = 0
        for p in self.program_block:
            print(f'{i} : {p}')
            i += 1

    def __init__(self, parser, scanner):
        # self.init_main_pb = 5
        self.parser = parser
        self.scope_record = sr.Scope(self)
        self.routine_dict = dict()
        self.routine_dict['#push_id'] = self.push_id
        self.routine_dict['#push_op'] = self.push_op
        self.routine_dict['#push_type'] = self.push_type
        self.routine_dict['#decl_id'] = self.decl_id
        self.routine_dict['#end_decl_var'] = self.end_decl_var
        self.routine_dict['#end_decl_arr'] = self.end_decl_arr
        self.routine_dict['#push_num'] = self.push_num
        self.routine_dict['#push_num_temp'] = self.push_num_temp
        self.routine_dict['#end_arr_param'] = self.end_arr_param
        self.routine_dict['#end_var_param'] = self.end_var_param
        self.routine_dict['#pop_exp'] = self.pop_exp
        self.routine_dict['#fun_declare_init'] = self.fun_declare_init
        self.routine_dict['#into_scope'] = self.into_scope
        self.routine_dict['#return_void'] = self.return_void
        self.routine_dict['#return_exp'] = self.return_exp
        self.routine_dict['#outo_scope'] = self.outo_scope
        self.routine_dict['#fun_declare_end'] = self.fun_declare_end
        self.routine_dict['#jump_over_func'] = self.jump_over_func
        self.routine_dict["#find_function"] = self.find_function
        self.routine_dict['#operate'] = self.operate
        self.routine_dict['#indirect_addr'] = self.indirect_addr
        self.routine_dict['#assign_to_local'] = self.assign_to_local
        self.routine_dict['#call_func'] = self.call_func
        self.routine_dict['#assign'] = self.assign
        self.routine_dict['#jp_main'] = self.jp_main
        self.routine_dict["#save_break"] = self.save_break
        self.routine_dict['#save_label'] = self.save_label
        self.routine_dict['#if_jpf'] = self.if_jpf
        self.routine_dict['#if_jpf_save_label'] = self.if_jpf_save_label
        self.routine_dict['#then_jp'] = self.then_jp
        self.routine_dict['#label'] = self.label
        self.routine_dict['#repeat_jump'] = self.repeat_jump
        self.routine_dict["save_break"] = self.save_break
        self.semantic_analyzer = sa.SemanticAnalyzer(scanner)
        self.semantic_analyzer.push("K")
        self.program_block = []
        self.mem = Memory(self)
        self.PC = self.mem.code_add

        self.BH = bh.Break()
        self.RT = bh.Return()
        self.function_to_call = []
        self.cond_jumps = []
        self.starting_block = self.PC
        self.first_time = True
        self.current_func_init = ''
        self.is_correct = False
        # self.add_command(Three_Address_Code(None, None, None, None))

    def get_last_fun(self):
        return self.function_to_call[len(self.function_to_call) - 1]

    def parse_token(self, token):
        lexeme = token.split(",")[1] if token != '$' else token
        lexeme = lexeme.replace(")", "")
        return (lexeme.strip())

    def generate_code(self, action, token):
        print("-----------------------------------------------------------------------------------------------")
        print(action, token)
        print("Error Handler: ")
        print(self.semantic_analyzer.error_handler)
        print("Semantic Stack: ")
        print(self.semantic_analyzer.semantic_stack)
        self.routine_dict.get(action)(self.parse_token(token))
        for error in self.semantic_analyzer.semantic_errors:
            print(error)
        # self.print_program_block()
        # print(self.semantic_analyzer.semantic_stack)
        print("Records: ")
        self.scope_record.print_records()
        print("Function Args: ")
        print(self.semantic_analyzer.functions_argument)
        # print(self.function_to_call)

    def decl_id(self, token):
        self.semantic_analyzer.push(token)

    def save_label(self, token):
        # self.semantic_analyzer.push(val)
        self.semantic_analyzer.push(self.PC)

    def if_jpf(self, token):
        index, cond = self.semantic_analyzer.pop(), self.semantic_analyzer.pop()
        self.update_command(index, Three_Address_Code2('JPF', cond, f'#{self.PC}', None, "if_jpf save label"))

    def if_jpf_save_label(self, token):
        index, cond = self.semantic_analyzer.pop(), self.semantic_analyzer.pop()
        self.semantic_analyzer.push(self.PC)

    def then_jp(self, token):
        index = self.semantic_analyzer.pop()

    def label(self, token):
        # self.semantic_analyzer.push(self.PC)
        self.BH.add_repeat()

    def repeat_jump(self, token):
        # cond = self.analyze_exp(self.semantic_analyzer.pop())
        # index = self.semantic_analyzer.pop()
        pass

    def save_break(self, token):
        if len(self.BH.q) == 0:
            self.semantic_analyzer.break_statement_error()
            return
        self.BH.add_break(self.PC)

    def assign_to_local(self, token):
        # val = self.analyze_exp(self.semantic_analyzer.pop())
        # offset = self.get_offset_temp()
        pass

    def assign(self, token):
        rhs_semantic, lhs_semantic = self.semantic_analyzer.error_handler.pop()[1], \
                                     self.semantic_analyzer.error_handler.pop()[1]
        if not ((rhs_semantic == 'int' and lhs_semantic == 'int') or (
                rhs_semantic == 'array' and lhs_semantic == 'array')):
            self.semantic_analyzer.type_mismatch_error(lhs_semantic, rhs_semantic)  # Semantic ERRORS


    def jp_main(self, token):
        r = self.scope_record.find_record('main')
        self.function_to_call.append(r)
        # self.call_func("a", if_main=True)

    def find_function(self, token):
        token = self.semantic_analyzer.pop()
        print(token)
        self.semantic_analyzer.function_to_call = token
        self.function_to_call.append(token)
        if token == "output":
            # self.function_to_call.append("output")
            self.semantic_analyzer.error_handler.append('call')
            return
        r = self.scope_record.find_record(token)
        self.semantic_analyzer.error_handler.append('call')
        # self.function_to_call.append(r)

    def call_func(self, token, if_main=False):
        fun = self.get_last_fun()
        r = self.scope_record.current_fun
        self.semantic_analyzer.function_to_call = self.function_to_call[-1]
        print('FUNCTIONS TO CALL')
        print(self.function_to_call, self.semantic_analyzer.function_to_call)
        self.semantic_analyzer.error_handler.append((r.lexeme, r.var_type, 'FUN'))
        if not if_main and self.semantic_analyzer.handle_argument_errors(): # Semantic ERRORS
            return
        if type(fun) == str and fun == "output":
            self.semantic_analyzer.push(f'0')
            self.function_to_call.pop()
            return

        self.function_to_call.pop()
        self.semantic_analyzer.error_handler.append((r.lexeme, 'int', r.type))


    def get_offset_temp(self):
        fun = self.scope_record.current_fun
        address = fun.update_local_var()
        return address

    def operate(self, token):
        rhs_semantic, lhs_semantic = self.semantic_analyzer.error_handler.pop()[1], self.semantic_analyzer.error_handler.pop()[1] # Semantic ERRORS
        if rhs_semantic != 'int' or lhs_semantic != 'int':
            self.semantic_analyzer.type_mismatch_error(lhs_semantic, rhs_semantic) # Semantic ERRORS
            return
        self.semantic_analyzer.error_handler.append(('temp', 'int', 'temp'))

    def indirect_addr(self, token):  # TODO anylie
        self.semantic_analyzer.error_handler.pop()
        lexeme = self.semantic_analyzer.error_handler.pop()
        self.semantic_analyzer.error_handler.append((lexeme[0]+'[]', 'int', lexeme[2]))
        # index, address = self.semantic_analyzer.pop(), self.semantic_analyzer.pop()

        # self.semantic_analyzer.push(f"@!{offset}")

    def return_void(self, token):
        pass

    def return_exp(self, token):
        pass

    def outo_scope(self, token):
        self.scope_record.delete_current_scope()

    def jump_over_func(self, token):
        pass

    def fun_declare_end(self, token):
        pass

    def into_scope(self, token):  # TODO
        self.scope_record.new_scope()

    def fun_declare_init(self, token):
        if self.first_time:
            self.starting_block = self.PC
            self.first_time = False
        print(self.semantic_analyzer.semantic_stack)
        lexeme, var_type = self.semantic_analyzer.pop(), self.semantic_analyzer.pop()
        print(lexeme, var_type)
        self.current_func_init = lexeme
        self.semantic_analyzer.functions_argument[lexeme] = [lexeme, var_type, 0, []]
        r = self.scope_record.insert_record(lexeme=lexeme, var_type=var_type, type="FUN", address=self.PC)
        self.scope_record.current_fun = r

    def end_arr_param(self, token):
        r = self.scope_record.get_last_record()
        r.type = "arg_arr"
        self.semantic_analyzer.functions_argument[self.scope_record.current_fun.lexeme][-1][-1] = ('array', r.lexeme)

    def end_var_param(self, token):
        lexeme, var_type = self.semantic_analyzer.pop(), self.semantic_analyzer.pop()
        if var_type == 'void':
            self.semantic_analyzer.void_type_error(lexeme)
            return
        fun = self.scope_record.current_fun
        address = fun.update_args()
        self.semantic_analyzer.update_function_args(self.current_func_init, lexeme, var_type) # Semantic ERRORS
        self.scope_record.insert_record(lexeme=lexeme, var_type=var_type, type="arg_var", address=address)

    def end_decl_arr(self, token):
        num, lexeme, var_type = self.semantic_analyzer.pop(), self.semantic_analyzer.pop(), self.semantic_analyzer.pop()
        if var_type == 'void':
            self.semantic_analyzer.void_type_error(lexeme)
            return
        # num = int(num.replace("#", ""))
        if self.scope_record.current_scope == 0:
            self.scope_record.insert_record(lexeme=lexeme, var_type=var_type, type="global_arr")
            return
        fun = self.scope_record.current_fun
        # offset = fun.update_local_var(num + 1)
        self.scope_record.insert_record(lexeme=lexeme, var_type=var_type, type="local_arr")
        return

    def end_decl_var(self, token):
        lexeme, var_type = self.semantic_analyzer.pop(), self.semantic_analyzer.pop()
        if var_type == 'void':
            self.semantic_analyzer.void_type_error(lexeme)
            return
        if self.scope_record.current_scope == 0:
            temp = self.mem.get_static_address()
            self.scope_record.insert_record(lexeme=lexeme, var_type=var_type, type="global_var", address=temp)
            return
        fun = self.scope_record.current_fun
        address = fun.update_local_var()
        self.scope_record.insert_record(lexeme=lexeme, var_type=var_type, type="local_var", address=address)
        return

    def push_type(self, token):
        self.semantic_analyzer.push(token)

    def push_op(self, token):
        self.semantic_analyzer.push(token)

    def push_num(self, token):
        self.semantic_analyzer.push(f'#{token}')

    def push_num_temp(self, token):
        num = int(token)
        self.semantic_analyzer.error_handler.append((num, 'int', 'NUM'))  # Semantic ERRORS
        # self.semantic_analyzer.push(f'{temp}')

    def pop_exp(self, token):
        self.semantic_analyzer.pop()

    def push_id(self, token):
        if token == "output":
            self.semantic_analyzer.push(token)
            return

        record = self.scope_record.find_record(token)
        if not record:
            self.semantic_analyzer.scoping_error(token)
            self.semantic_analyzer.error_handler.append(('Not-found', 'int', '$'))
            # self.scope_record.insert_record(token, 0, 'not-available', 'int')
            return

        if record.scope_num == 0:
            if record.type == 'FUN':
                self.semantic_analyzer.push(token)
            else:
                self.semantic_analyzer.error_handler.append((record.lexeme, record.var_type if 'arr' not in record.type else 'array', record.type))
                self.semantic_analyzer.push(record.address)
        else:
            print('Here')
            self.semantic_analyzer.error_handler.append((record.lexeme, record.var_type if 'arr' not in record.type else 'array', record.type))
            self.semantic_analyzer.push(f'!{record.address}')
