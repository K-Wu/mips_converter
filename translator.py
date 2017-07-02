#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# attempt to translate machine code in rom.v into (almost) mips assembly
from __future__ import print_function

import converter

# OPCODE_OFFSET=26
# FUNCT_NUMBITS=6
ROM_FILENAME = "rom_ori.v"
R_INSTRUCTION_FUNCT = {val[0]: instr for instr, val in converter.R_INSTRUCTIONS.items()}  # 格式9:"jalr"

REGISTER_NAME = {i: register_name for i, register_name in enumerate(converter.REGISTER_NAME)}
J_INSTRUCTION_OPCODE = {opcode: instr for instr, opcode in converter.J_INSTRUCTIONS.items()}
SL_INSTRUCTION_OPCODE = {opcode: instr for instr, opcode in converter.SL_INSTRUCTIONS.items()}
I_INSTRUCTION_OPCODE = {val[0]: instr for instr, val in converter.I_INSTRUCTIONS.items()}


def load_machine_code(filename):
    machine_codes = []
    with open(filename) as fd:
        lines = fd.readlines()  ##参数里写了ROM_FILENAME后改成了filename,后改成了fd...
        code_lines_ind = []
        for i in range(len(lines)):
            if lines[i].find("'h") != -1:
                begin = lines[i].find("'h") + 2  ##'h是两个字符
                end = lines[i].rfind(";")  ##没有考虑到\n
                if end - begin == 8:
                    machine_codes.append(lines[i][begin:end])
                else:
                    assert end - begin == 9, str(i)
                    machine_code = lines[i][begin:begin + 4] + lines[i][begin + 5:begin + 9]
                    machine_codes.append(machine_code)

    return machine_codes


def get_register_name(register_id, returnName=False):
    # 输入寄存器编号，输出寄存器字符串
    if returnName:
        return "$" + REGISTER_NAME[register_id]
    else:
        return "$" + str(register_id)


def translate_single_line(machine_code, address_ind):
    machine_code = int(machine_code, 16)
    opcode = machine_code >> converter.OPCODE_OFFSET
    line = ""
    if (opcode == 0):  # R instruction
        funct = machine_code % (1 << converter.FUNC_NUMBITS)
        instr = ""
        try:
            instr = R_INSTRUCTION_FUNCT[funct]
        except KeyError:
            return "<unknown instruction>"
        param_num = max(converter.R_INSTRUCTIONS[instr][1:]) + 1
        params = [""] * param_num
        for i, param_position in enumerate(converter.R_INSTRUCTIONS[instr][1:]):
            if param_position == -1:
                continue
            param_code = machine_code / (1 << converter.R_OFFSETS[i + 1]) % (1 << converter.R_NUMBITS[i + 1])
            if converter.R_TYPES[i + 1] == "register":
                params[param_position] = get_register_name(param_code)
            else:
                params[param_position] = ("0x{:0" + "{}".format(converter.R_NUMBITS[i]) + "X}").format(param_code)
        line = instr + " " + " ".join([str(item) for item in params])
    elif opcode in I_INSTRUCTION_OPCODE:
        instr = I_INSTRUCTION_OPCODE[opcode]
        param_num = max(converter.I_INSTRUCTIONS[instr][1:]) + 1
        params = [""] * param_num
        for i, param_position in enumerate(converter.I_INSTRUCTIONS[instr][1:]):
            if param_position == -1:
                continue
            param_code = machine_code / (1 << converter.I_OFFSETS[i + 1]) % (1 << converter.I_NUMBITS[i + 1])
            if converter.I_TYPES[i + 1] == "register":
                params[param_position] = get_register_name(param_code)
            else:
                params[param_position] = ("0x{:0" + "{}".format(converter.R_NUMBITS[i]) + "X}").format(param_code)
        line = instr + " " + " ".join([str(item) for item in params])
    elif opcode in J_INSTRUCTION_OPCODE:
        instr = J_INSTRUCTION_OPCODE[opcode]
        param_code = machine_code % (1 << 26)
        address = param_code << 2
        line = instr + " 0x{:08X}".format(param_code)
    elif opcode in SL_INSTRUCTION_OPCODE:
        instr = SL_INSTRUCTION_OPCODE[opcode]
        # rt,offset 只显示offset
        rt_id = machine_code / (1 << converter.RT_OFFSET) % (1 << converter.REG_NUMBITS)
        is_SLW=False
        rs_id=-1
        if SL_INSTRUCTION_OPCODE[opcode] in {"sw","lw"}:
            is_SLW=True
            rs_id=machine_code / (1 << converter.RS_OFFSET) % (1 << converter.REG_NUMBITS)
        offset = machine_code % (1 << converter.IMM_NUMBITS)
        line = instr + " " + get_register_name(rt_id) + " " + "0x{:04X}".format(offset)
        if is_SLW:
            line+="(${})".format(rs_id)
    else:
        line = "<unknown instruction>"
    return line


def translate(machine_codes):
    mips_assembly_lines = []
    for line_ind, machine_code in enumerate(machine_codes):
        line = translate_single_line(machine_code, line_ind)
        mips_assembly_lines.append(line)
    return mips_assembly_lines


if __name__ == "__main__":
    machine_codes = load_machine_code(ROM_FILENAME)
    b=translate(["02748822"])
    #a=translate(["2748825"])
    mips_assembly_lines = translate(machine_codes)
    ROM_OUT_FILENAME = "rom_ori.out"
    with open(ROM_OUT_FILENAME, 'w') as fd:
        for line in mips_assembly_lines:
            fd.write(line)
            fd.write("\n")
    pass
