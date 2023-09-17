from scope_records import scope_record as sr
from code_gen import code_generator
from code_gen import code_generator as CG
from collections import namedtuple
Three_Address_Code = namedtuple('ThreeAddressCode', 'op y z x')


class Memory():
    def __init__(self, code_gen):
        self.code_add = 0
        self.activation_record = 10008  # save activation record # always full
        self.static_data = 5000
        self.return_val = 10000
        self.return_add = 9996
        self.code_g = code_gen
    def initial(self):
        self.code_g.add_command(Three_Address_Code("ASSIGN", f"#{0}", self.return_add, None))
        self.code_g.add_command(code_generator.Three_Address_Code("ASSIGN", f"#{0}", self.return_val, None))
        self.code_g.add_command(
            code_generator.Three_Address_Code("ASSIGN", f"#{self.activation_record + 4}", self.activation_record, None))

    def get_static_address(self, skip=4):
        # self.get_program_block()
        # self.code_g.program_block.append(code_generator.Three_Address_Code("ASSIGN", "#0", self.static_data, None))
        self.static_data += skip
        return self.static_data - skip

    def get_front_code(self):
        return self.code_add
