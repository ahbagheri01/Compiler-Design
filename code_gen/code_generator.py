from semantic_analyzer import semantic_analyzer as sa
from code_gen.Memory_handler import Memory
from code_gen.semantic import Semantic
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


class CodeGenerator:
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
        self.mem.initial()
        self.semantic = Semantic(parser, scanner)
        self.BH = bh.Break()
        self.RT = bh.Return()
        self.function_to_call = []
        self.cond_jumps = []
        self.starting_block = self.PC
        self.first_time = True
        self.current_func_init = ''
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
        self.semantic.generate_code(action, token)
        if len(self.semantic.semantic_analyzer.semantic_errors) == 0:
            self.routine_dict.get(action)(self.parse_token(token))
        self.print_program_block()
        print(self.semantic_analyzer.semantic_stack)
        self.scope_record.print_records()
        print(self.function_to_call)

    def decl_id(self, token):
        self.semantic_analyzer.push(token)

    def save_label(self, token):
        val = self.analyze_exp(self.semantic_analyzer.pop())
        self.semantic_analyzer.push(val)
        self.semantic_analyzer.push(self.PC)
        # self.cond_jumps.append(self.PC)
        self.add_command(Three_Address_Code2('JPF', val, '?', None, "save_label JPF"))

    def if_jpf(self, token):
        index, cond = self.semantic_analyzer.pop(), self.semantic_analyzer.pop()
        self.update_command(index, Three_Address_Code2('JPF', cond, f'#{self.PC}', None, "if_jpf save label"))

    def if_jpf_save_label(self, token):
        index, cond = self.semantic_analyzer.pop(), self.semantic_analyzer.pop()
        self.semantic_analyzer.push(self.PC)
        self.add_command(Three_Address_Code2('JP', '?', f'#{index}', None, "if_jpf_save_label"))
        self.update_command(index, Three_Address_Code2('JPF', cond, f'#{self.PC}', None, "if_jpf_save_label JPF"))

        pass

    def then_jp(self, token):
        index = self.semantic_analyzer.pop()
        self.update_command(index, Three_Address_Code2('JP', f'#{self.PC}', None, None, "then JP"))

    def label(self, token):
        self.semantic_analyzer.push(self.PC)
        self.BH.add_repeat()

    def repeat_jump(self, token):
        cond = self.analyze_exp(self.semantic_analyzer.pop())
        index = self.semantic_analyzer.pop()
        self.add_command(Three_Address_Code2('JPF', cond, index, None, "repeat_jump "))
        break_list = self.BH.get_breaks_address()
        for br_index in break_list:
            self.update_command(br_index, Three_Address_Code2('JP', self.PC, None, None, "filled for break"))

    def save_break(self, token):
        self.BH.add_break(self.PC)
        self.add_command(Three_Address_Code2('?', None, None, None, "save_break"))

    def assign_to_local(self, token):
        val = self.analyze_exp(self.semantic_analyzer.pop())
        offset = self.get_offset_temp()
        temp = self.mem.get_static_address()
        self.add_command(
            Three_Address_Code2("ADD", f"#{(offset * 4)}", self.mem.activation_record, temp, "assign to local"))
        self.add_command(Three_Address_Code2("ASSIGN", f'{val}', f'@{temp}', None, "assign to local"))
        self.semantic_analyzer.push(f'!{offset}')

        # offset = self.get_offset_temp()
        pass

    def assign(self, token):
        rhs, lhs = self.semantic_analyzer.pop(), self.semantic_analyzer.pop()
        rhsA, lhsA = self.analyze_exp(rhs), self.analyze_exp(lhs, right=False)
        self.add_command(Three_Address_Code2("ASSIGN", rhsA, lhsA, None, "assign"))
        self.semantic_analyzer.push(lhs)

    def jp_main(self, token):

        r = self.scope_record.find_record('main')
        self.update_command(self.starting_block, Three_Address_Code2("JP", f"#{r.address}", None, None, "jp main"))
        self.function_to_call.append(r)
        self.call_func("a", if_main=True)
        # Whatever we do in call_func

    def find_function(self, token):
        token = self.semantic_analyzer.pop()
        if token == "output":
            self.function_to_call.append("output")
            return
        r = self.scope_record.find_record(token)
        self.function_to_call.append(r)

    def call_func(self, token, if_main=False):
        fun = self.get_last_fun()
        if type(fun) == str and fun == "output":
            value_to_print = self.analyze_exp(self.semantic_analyzer.pop())
            self.add_command(Three_Address_Code2(
                "PRINT", value_to_print, None, None, "print"))
            self.semantic_analyzer.push(f'void_error')
            self.function_to_call.pop()
            return
        arg_num = self.get_last_fun().args
        offset = self.scope_record.current_fun.local_var + 1
        arg_arr = []
        for i in range(arg_num):
            arg_arr.append(self.semantic_analyzer.pop())
        arg_arr = arg_arr[::-1]
        save_address = self.PC
        self.add_command(Three_Address_Code("?", None, None, None))  # offset + 1 #TODO return
        self.add_command(Three_Address_Code("?", None, None, None))  # offset + 1 #TODO return
        self.add_command(Three_Address_Code("?", None, None, None))  # offset + 1 #TODO return
        self.add_command(Three_Address_Code("?", None, None, None))  # offset + 1 #TODO return
        temp = self.mem.get_static_address()
        for (i, a) in enumerate(arg_arr):
            self.add_command(
                Three_Address_Code2("ADD", f'#{(offset + i + 2) * 4}', self.mem.activation_record, temp, "pass arg"))

            self.add_command(Three_Address_Code2("ASSIGN", self.analyze_exp(a), f'@{temp}', None, "pass arg"))
        self.update_command(save_address + 2,
                            Three_Address_Code2("ADD", f'#{(1 + offset) * 4}', self.mem.activation_record, f'{temp}',
                                                "for record get offset"))
        self.update_command(save_address + 3,
                            Three_Address_Code2("ASSIGN", self.mem.activation_record, f'@{temp}',
                                                None, "save activation record"))  # save activation  record in stack
        self.add_command(
            Three_Address_Code2("ADD", f'#{(offset + 1) * 4}', self.mem.activation_record, temp, "reverse acc"))
        self.add_command(Three_Address_Code2("ASSIGN", temp, self.mem.activation_record,
                                             None,
                                             "save new acc to acc"))  # save new activation  record in activation record
        self.add_command(Three_Address_Code("JP", self.get_last_fun().address, None, None))
        self.update_command(save_address,
                            Three_Address_Code2("ADD", f'#{offset * 4}', f'{self.mem.activation_record}', temp,
                                                "return add im temp"))
        self.update_command(save_address + 1,
                            Three_Address_Code2("ASSIGN", f'#{self.PC}', f'@{temp}', None,
                                                "set return add to stack"))  # save return address
        self.add_command(
            Three_Address_Code2("ASSIGN", f'@{self.mem.activation_record}', self.mem.activation_record, None,
                                "return acc to acc"))
        offset = self.get_offset_temp()
        self.add_command(
            Three_Address_Code2("ADD", f"#{offset * 4}", self.mem.activation_record, temp, "get local for return "))
        self.add_command(
            Three_Address_Code2("ASSIGN", f'{self.mem.return_val}', f'@{temp}', None, "set return val to local"))
        if if_main:
            self.add_command(Three_Address_Code("JP", "#5000000000000", None, None))
        if fun.var_type == "void":
            self.semantic_analyzer.push(f'void_error')
        else:
            self.semantic_analyzer.push(f'!{offset}')
        self.function_to_call.pop()

    def analyze_exp(self, exp, right=True):  # TODO just for read
        if "!" in str(exp):
            temp = self.mem.get_static_address()
            exp = exp.replace("!", "")
            if "@" in exp:
                exp = int(exp.replace("@", ""))
                exp = int(exp)
                self.add_command(Three_Address_Code2("ADD", f'#{exp * 4}', self.mem.activation_record, temp, "analyze"))
                self.add_command(Three_Address_Code2("ASSIGN", f'@{temp}', temp, None, "analyze"))
                if right:
                    self.add_command(Three_Address_Code2("ASSIGN", f'@{temp}', temp, None, "analyze"))
                    return temp
                return f'@{temp}'
            exp = int(exp)
            self.add_command(Three_Address_Code2("ADD", f'#{exp * 4}', self.mem.activation_record, temp, "analyze"))
            if not right:
                return f'@{temp}'
            self.add_command(Three_Address_Code2("ASSIGN", f'@{temp}', temp, None, "analyze"))
            return f'{temp}'
        elif right:
            temp = self.mem.get_static_address()
            self.add_command(Three_Address_Code2("ASSIGN", exp, temp, None, "analyze"))
            return temp
        return exp

    def get_offset_temp(self):
        fun = self.scope_record.current_fun
        address = fun.update_local_var()
        return address

    def operate(self, token):
        rhs, op, lhs = self.semantic_analyzer.pop(), self.semantic_analyzer.pop(), self.semantic_analyzer.pop()
        op = op.strip()
        offset = self.get_offset_temp()
        operation = ops[op]
        temp = self.mem.get_static_address()
        rhs, lhs = self.analyze_exp(rhs), self.analyze_exp(lhs)
        self.add_command(Three_Address_Code("ADD", f"#{offset * 4}", self.mem.activation_record, temp))

        self.add_command(Three_Address_Code(operation, lhs, rhs, f'@{temp}'))
        self.semantic_analyzer.push(f'!{offset}')

    def indirect_addr(self, token):  # TODO anylie
        index, address = self.semantic_analyzer.pop(), self.semantic_analyzer.pop()
        index = self.analyze_exp(index)
        address = self.analyze_exp(address)
        offset = self.get_offset_temp()
        temp2 = self.mem.get_static_address()
        self.add_command(Three_Address_Code("MULT", index, f'#{4}', temp2))
        self.add_command(Three_Address_Code("ADD", temp2, address, temp2))
        temp = self.mem.get_static_address()
        self.add_command(Three_Address_Code("ADD", f"#{offset * 4}", self.mem.activation_record, temp))
        self.add_command(Three_Address_Code("ASSIGN", temp2, f'@{temp}', None))
        self.semantic_analyzer.push(f"@!{offset}")

    def return_void(self, token):
        self.RT.add_return(self.PC)
        self.add_command(Three_Address_Code("JP", "?", None, None))


    def return_exp(self, token):
        exp = self.semantic_analyzer.pop()
        add = self.analyze_exp(exp)
        self.add_command(Three_Address_Code("ASSIGN", add, self.mem.return_val, None))
        self.RT.add_return(self.PC)
        self.add_command(Three_Address_Code("JP", "?", None, None))

    def outo_scope(self, token):
        for index in self.RT.q:
            self.update_command(index, Three_Address_Code("JP", self.PC, None, None))  # TODO fill return packing
        temp = self.mem.get_static_address()
        self.add_command(Three_Address_Code2("SUB", self.mem.activation_record, "#4", temp, "get access to return add"))
        self.add_command(Three_Address_Code2("ASSIGN", f"@{temp}", temp, None, "put return add to temp"))
        self.add_command(Three_Address_Code2("JP", f'@{temp}', None, None, "JP retrun add"))  # TODO jump return addres
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
            self.add_command(Three_Address_Code(None, None, None, None))
            self.first_time = False
        lexeme, var_type = self.semantic_analyzer.pop(), self.semantic_analyzer.pop()
        r = self.scope_record.insert_record(lexeme=lexeme, var_type=var_type, type="FUN", address=self.PC)
        self.scope_record.current_fun = r

    def end_arr_param(self, token):
        r = self.scope_record.get_last_record()
        r.type = "arg_arr"
        # lexeme, var_type = self.semantic_analyzer.pop(), self.semantic_analyzer.pop()
        # fun = self.scope_record.current_fun
        # address = fun.update_args()
        # self.scope_record.insert_record(lexeme=lexeme, var_type=var_type, type="arg_arr", address=address)

    def end_var_param(self, token):

        lexeme, var_type = self.semantic_analyzer.pop(), self.semantic_analyzer.pop()
        fun = self.scope_record.current_fun
        address = fun.update_args()
        self.scope_record.insert_record(lexeme=lexeme, var_type=var_type, type="arg_var", address=address)

    def end_decl_arr(self, token):
        num, lexeme, var_type = self.semantic_analyzer.pop(), self.semantic_analyzer.pop(), self.semantic_analyzer.pop()
        num = int(num.replace("#", ""))
        if self.scope_record.current_scope == 0:
            temp = self.mem.get_static_address()
            self.scope_record.insert_record(lexeme=lexeme, var_type=var_type, type="global_arr", address=temp, size=num)
            self.add_command(Three_Address_Code("ASSIGN", f"#{temp + 4}", temp, None))
            for i in range(0, num):
                temp = self.mem.get_static_address()
                self.add_command(Three_Address_Code("ASSIGN", "#0", temp, None))
            return
        fun = self.scope_record.current_fun
        offset = fun.update_local_var(num + 1)
        self.scope_record.insert_record(lexeme=lexeme, var_type=var_type, type="local_arr", address=offset)
        temp = self.mem.get_static_address()
        temp_2 = self.mem.get_static_address()
        self.add_command(Three_Address_Code("ADD", f"#{(offset * 4)}", self.mem.activation_record, temp))
        self.add_command(Three_Address_Code("ADD", f"#4", temp, temp_2))
        self.add_command(Three_Address_Code("ASSIGN", f'{temp_2}', f'@{temp}', None))
        for i in range(1, num + 1):
            self.add_command(Three_Address_Code("ADD", f"#{(offset + i) * 4}", self.mem.activation_record, temp))
            self.add_command(Three_Address_Code("ASSIGN", "#0", f'@{temp}', None))
        return

    def end_decl_var(self, token):
        lexeme, var_type = self.semantic_analyzer.pop(), self.semantic_analyzer.pop()
        if self.scope_record.current_scope == 0:
            temp = self.mem.get_static_address()
            self.scope_record.insert_record(lexeme=lexeme, var_type=var_type, type="global_var", address=temp)
            self.add_command(Three_Address_Code("ASSIGN", "#0", temp, None))
            return
        fun = self.scope_record.current_fun
        address = fun.update_local_var()
        self.scope_record.insert_record(lexeme=lexeme, var_type=var_type, type="local_var", address=address)
        temp = self.mem.get_static_address()
        self.add_command(Three_Address_Code("ADD", f"#{address * 4}", self.mem.activation_record, temp))
        self.add_command(Three_Address_Code("ASSIGN", "#0", f'@{temp}', None))
        return

    def add_command(self, tp):
        self.program_block.append(tp)
        if self.PC == 212:
            print("here")
        self.PC += 1

    def update_command(self, index, tp):
        self.program_block[int(index)] = tp

    def get_command(self, index):
        return self.program_block[index]

    def push_type(self, token):
        self.semantic_analyzer.push(token)

    def push_op(self, token):
        self.semantic_analyzer.push(token)

    def push_num(self, token):
        self.semantic_analyzer.push(f'#{token}')

    def push_num_temp(self, token):
        num = int(token)
        temp = self.mem.get_static_address()
        self.add_command(Three_Address_Code('ASSIGN', f'#{num}', temp, None))
        self.semantic_analyzer.push(f'{temp}')

    def pop_exp(self, token):
        self.semantic_analyzer.pop()

    def push_id(self, token):
        if token == "output":
            self.semantic_analyzer.push(token)
            return

        record = self.scope_record.find_record(token)
        if record.scope_num == 0:
            if record.type == 'FUN':
                self.semantic_analyzer.push(token)
            else:
                self.semantic_analyzer.push(record.address)
        else:
            self.semantic_analyzer.push(f'!{record.address}')