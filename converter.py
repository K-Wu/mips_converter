#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# 32位MIPS指令各组成部分的偏移量
OPCODE_OFFSET = 26
RS_OFFSET = 21
RT_OFFSET = 16
RD_OFFSET = 11
SHAMT_OFFSET = 6
FUNC_OFFSET = 0
IMM_OFFSET = 0

# 寄存器名称和编号的对应关系
REGISTER_NAME = ["zero", "at", "v0", "v1", "a0", "a1", "a2", "a3", "t0", "t1",  # 0-9
                 "t2", "t3", "t4", "t5", "t6", "t7", "s0", "s1", "s2", "s3",  # 10-19
                 "s4", "s5", "s6", "s7", "t8", "t9", "k0", "k1", "gp", "sp",  # 20-29
                 "fp", "ra"
                 ]
REGISTER_NAME_ID = {name: id for id, name in enumerate(REGISTER_NAME)}

# 需要重定位的指令
RELOCATION = {
    "jalr", "jr",
    "beq", "bgtz", "blez", "bltz", "bne",  # TODO:check
    "j", "jal"
}

# R指令的func code，各参数的位置和偏移量
# TODO:检查立即数位数，是不是R,存取指令,B16位，J26位，
R_OFFSETS = [FUNC_OFFSET, RS_OFFSET, RT_OFFSET, RD_OFFSET, SHAMT_OFFSET]
FUNC_NUMBITS=6
REG_NUMBITS=5
SHAMT_NUMBITS=5
R_NUMBITS = [FUNC_NUMBITS,REG_NUMBITS,REG_NUMBITS,REG_NUMBITS,SHAMT_NUMBITS]#for translator
R_TYPES = ["should not appear", "register", "register", "register", "shamt"]
R_INSTRUCTIONS = {
    # funccode,rs position(in parameters),rt position,rd position, shamt position
    "jalr": [9, 0, -1, 1, -1],
    "jr": [8, 0, -1, -1, -1],
    "slt": [0x2a, 1, 2, 0, -1],
    "xor": [0x26, 1, 2, 0, -1],
    "subu": [0x23, 1, 2, 0, -1],
    "sub": [0x22, 1, 2, 0, -1],
    "srl": [2, -1, 1, 0, 2],
    "sra": [3, -1, 1, 0, 2],
    "sll": [0, -1, 1, 0, 2],
    "or": [0x25, 1, 2, 0, -1],
    "nor": [0x27, 1, 2, 0, -1],
    "and": [0x20, 1, 2, 0, -1],
    "addu": [0x20, 1, 2, 0, -1],#注意addu指令格式是 add $d,$s,$t，不带立即数
    "add": [0x20, 1, 2, 0, -1],
    "sltu": [0x2b, 1, 2, 0, -1],
}

# I指令的OPCODE
##各参数在指令后的位置并不是固定的，b系列的rs和rt与一般指令的位置正好相反）
#依样画葫芦
IMM_NUMBITS=16
OPCODE_NUMBITS=6
I_OFFSETS = [OPCODE_OFFSET, RS_OFFSET, RT_OFFSET, IMM_OFFSET]
I_NUMBITS = [OPCODE_NUMBITS,REG_NUMBITS,REG_NUMBITS,IMM_NUMBITS]
I_TYPES = ["should not appear", "register", "register", "immediate"]
I_INSTRUCTIONS = {
    # OPCODE.
    ## rs position,rt position,imm position
    "addi": [8,1,0,2],
    "addiu": [9,1,0,2],
    "andi": [0xc,1,0,2],
    "slti": [0xa,1,0,2],
    "sltiu": [0xb,1,0,2],
    "beq": [4,0,1,2],  #
    "bgtz": [7,0,1,2],  #
    "blez": [6,0,1,2],  #
    "bltz": [1,0,1,2],  #
    "bne": [5,0,1,2]  #
}
# TODO:注意不同指令地址指定，有的是2开始，有的是0开始，把这个放在哪里实现？
# 读存指令的OPCODE，各参数的位置是固定的
SL_INSTRUCTIONS = {
    # OPCODE

    "lui": 0xf,# rs,rt,imm should be -1,0,1
    "lw": 0x23,## 特殊的表示方式
    "sw": 0x2b ## 特殊的寄存器、立即数表示方式
}
SL_REGISTER_INSTRUCTIONS ={
    "sw","lw"#会出现4($sp)这种操作的指令集合
}
# J指令的OPCODE，后26位为地址偏移
J_INSTRUCTIONS = {
    # OPCODE
    "j": 2,  #
    "jal": 3,  #
}
# 分支、跳转指令的地址位数
BJ_MODULUS = {
    "beq": 16,
    "bgtz": 16,
    "blez": 16,
    "bltz": 16,
    "bne": 16,
    "j": 26,
    "jal": 26
}
# 如果四种指令出现立即数，那么位数是
IMM_MODULUS = {
    "J": 26,
    "SL": 16,
    "I": 16,
    "R": 16
}


def get_instruction_type(instruction):
    """
    给一个str表示的指令，返回这个指令的参数和常数信息。
    所谓参数信息，就是这个指令后面会跟的寄存器、立即数有几个，相对位置是什么；
    所谓常数信息，就是这个指令的OPCODE或者FuncCode是什么，为通用性，将这二者统一，因此返回常数和常数的偏移量
    instruction_type应该是J,SL,I,R中的一种,
    返回param_number,[(param,param_type,param_offset)],(constant,constant_offset),instruction_type
    :param instruction: str
    :return: int, list, tuple, str
    """

    immediate_string = "immediate"  # 将区分立即数和待重定向成地址的label，后者在第一遍循环时还无法知道目标地址
    if instruction in RELOCATION:
        immediate_string = "relocate"
    if instruction in J_INSTRUCTIONS:
        assert immediate_string == "relocate", "J instruction should have relocate"
        return 1, [(0, "relocate", IMM_OFFSET)], (J_INSTRUCTIONS[instruction], OPCODE_OFFSET), "J"
    elif instruction in SL_INSTRUCTIONS:
        if instruction in SL_REGISTER_INSTRUCTIONS:
            ##没有考虑到sw,lw中4($sp)这样的操作
            return 2, [(0, "register", RT_OFFSET), (1, "SL_register", (RS_OFFSET,IMM_OFFSET))], (
            SL_INSTRUCTIONS[instruction], OPCODE_OFFSET), "SL"
        else:
            return 2, [(0, "register", RT_OFFSET), (1, "register", IMM_OFFSET)], (
                SL_INSTRUCTIONS[instruction], OPCODE_OFFSET), "SL"
    elif instruction in I_INSTRUCTIONS:
        param_offsets_pair = [(I_INSTRUCTIONS[instruction][i], I_TYPES[i], I_OFFSETS[i]) for i in
                              range(1, len(I_OFFSETS)-1) if I_INSTRUCTIONS[instruction][i] != -1]#先加上两个寄存器
        param_offsets_pair.append((2, immediate_string, IMM_OFFSET))#再加上立即数
        return 3, param_offsets_pair, (I_INSTRUCTIONS[instruction][0], OPCODE_OFFSET), "I"

    elif instruction in R_INSTRUCTIONS:
        param_number = max(R_INSTRUCTIONS[instruction][1:]) + 1
        param_offsets_pair = [(R_INSTRUCTIONS[instruction][i], R_TYPES[i], R_OFFSETS[i]) for i in
                              range(1, len(R_OFFSETS)) if R_INSTRUCTIONS[instruction][i] != -1]
        return param_number, param_offsets_pair, (R_INSTRUCTIONS[instruction][0], FUNC_OFFSET), "R"
    raise ValueError, "instruction " + instruction + " is unknown and cannot give param,constant information correctly"

def decode_sl_register(reg_str):
    """
    专门用来解析SL指令的第二个寄存器，通常为4($sp)种种。
    返回的第一个值为寄存器编号，第二个值为立即数
    :param reg_str: str
    :return: int, int
    """
    #有三种可能：只有立即数（没有括号），只有寄存器（有括号），又有立即数又有寄存器（有括号）。虽然第一种只在MARS中看到过
    left_par_pos=reg_str.find("(")
    if left_par_pos==-1:
        return 0, int(reg_str)
    if left_par_pos==0:
        return decode_register(reg_str),0
    return decode_register(reg_str[left_par_pos+1:-1]),int(reg_str[0:left_par_pos])

def decode_register(reg_str):
    """
    输入寄存器字符串"$s1"，输出对应的机器码
    :param reg_str:
    :return:
    """
    if not reg_str[1].isalpha():  # 输入是"$1","$2","$3"
        return int(reg_str[1:])
    else:  # 输入是"s1","t1"这种
        return REGISTER_NAME_ID[reg_str[1:]]
    pass


def read_clean_code(filename):
    """
    读指定asm文件，返回list，每个元素为指令/寄存器/立即数
    :param filename:str
    :return: list
    """
    raw_codeline = []
    with open(filename) as fd:
        raw_codeline = fd.readlines()
    code_without_comma = []
    for i, line in enumerate(raw_codeline):
        # TODO: supppose string does not exist
        line = line.strip()
        comment_position = -1
        # 找到注释位置
        for j in range(len(line)):
            if line[j] == "#":
                comment_position = j
                break
        # 如果注释存在，那么注释及其之后的内容全部去掉
        if comment_position >= 0:  ##这里此前漏加了等号
            code_without_comma.extend(line[0:comment_position].split(","))
        else:
            code_without_comma.extend(line.split(","))  # 先将每行的内容去掉逗号
    clean_code = []
    for i, code_seg in enumerate(code_without_comma):
        clean_code.extend(code_without_comma[i].split())  # 再将每行的内容去掉空格，制表符等字符
    return clean_code


def get_negint_represent(number, num_bits):
    """
    输入一个负数，根据补码计算规则返回指定位数下的表示
    :param number: int
    :param num_bits: int
    :return: int
    """
    if number >= 0:  # 不对非负进行操作
        return number
    return ~(-number) % (1 << num_bits) + 1##漏掉了负号，应该先得到绝对值，再来一波bit manipulation
                                            ##refactor的时候漏掉了+1


TEXT_ADDRESS_START_POSITION = 0x00000000

def convert_assembly(clean_code):
    """
    将clean_code转换为机器码，组织格式为
    {address:{"machine code":machine_code,("relocation":relocation,etc.)}}
    :return: dict
    """

    i = 0

    # 将指令转换为{address:{"machine_code":machine_code(,"relocation":relocation,"tag":tag)}}
    converted_instruction = {}
    tag_address = {}  # tag_name:address
    text_address_relocate = []  # 记录了需要重定向的指令的地址
    address = TEXT_ADDRESS_START_POSITION
    while (i < len(clean_code) - 1):
        converted_instruction[address] = {}
        # 遇到了一个标签
        if clean_code[i].find(":") != -1:
            converted_instruction[address]["tag"] = clean_code[i][0:-1]
            tag_address[clean_code[i][0:-1]] = address
            i += 1
            continue
        # 遇到了一个指令
        converted_instruction[address]["instruction"] = clean_code[i]
        param_number, param_types_offsets, (constant, constant_offset), instruction_type = get_instruction_type(
                clean_code[i])
        converted_instruction[address]["instruction_type"] = instruction_type
        machine_code = constant << constant_offset
        for param, param_type, param_offset in param_types_offsets:
            if param_type == "immediate" or param_type == "shamt":  ##写成param_type=="immediate" or "shamt"是不行的
                num_specified = int(clean_code[i + param + 1])
                ##第一次写漏写了立即数取反

                if num_specified < 0:
                    assert param_type == "immediate", "should not have negative number as shamt"  # 只可能负数出现在imm，而不是shamt
                    num_specified=get_negint_represent(num_specified, IMM_MODULUS[converted_instruction[address]["instruction_type"]])
                    num_specified_alternative = ~(-num_specified) % (##漏掉了负号，应该先得到绝对值，再来一波bit manipulation
                    1 << IMM_MODULUS[converted_instruction[address]["instruction_type"]])+1
                    assert num_specified==num_specified_alternative
                machine_code += num_specified << param_offset
            elif param_type == "register":
                machine_code += decode_register(clean_code[i + param + 1]) << param_offset
            elif param_type == "SL_register":
                reg_no, imm = decode_sl_register(clean_code[i+param+1])
                machine_code+=reg_no<<param_offset[0]
                machine_code+=imm<<param_offset[1]
            elif param_type == "relocate":
                converted_instruction[address]["relocate"] = clean_code[i + param + 1]
                text_address_relocate.append(address)
                converted_instruction[address]["relocate_type"] = clean_code[i]  # TODO:remove this and following line
                assert converted_instruction[address]["relocate_type"] == converted_instruction[address]["instruction"]
            else:
                raise ValueError, "unexpected param_type"
        converted_instruction[address]["machine_code"] = machine_code
        i += param_number  # 寄存器/立即数
        # 解析下一条指令
        i += 1
        address += 4

    # 对跳转指令进行重定向，注意不同指令的差异：
    # B开头的是[17:2]位，jr,jal也是，TODO:似乎都是？
    for text_address in text_address_relocate:##这一步一开始直接跳过了，原因在第一次循环时没有向这个数组加入东西
        destination = tag_address[converted_instruction[text_address]["relocate"]]##写成了address
        converted_instruction[text_address]["relocate"] = destination
        # 对重定向的地址的机器码加上地址（立即数部分）：
        ##没有考虑B指令应该是跳转地址和PC+4的差，并注意还是需要处理负偏移
        if converted_instruction[text_address]["instruction_type"] == "I":#分支指令
            machine_code_offset=((destination-text_address-4)>>2)%(1<<16)
            if machine_code_offset<0:
                machine_code_offset=get_negint_represent(machine_code_offset, 16)
            assert IMM_MODULUS[converted_instruction[text_address]["instruction_type"]] == 16
        else:#跳转指令
            machine_code_offset = (destination >> 2) % (1 << 26)  ##写成了直接对IMM_MODULUS取模，但1<<后者才是真正的模值
            assert IMM_MODULUS[converted_instruction[text_address]["instruction_type"]]==26
        assert BJ_MODULUS[converted_instruction[text_address]["instruction"]] == IMM_MODULUS[
            converted_instruction[text_address]["instruction_type"]]  # TODO：去除BJ_MODUUS,条件是，立即数只有J是26位，其它全部16位
        converted_instruction[text_address]["machine_code"] += machine_code_offset << 0
    return converted_instruction


def nice_print(converted_instruction):
    string = ""
    for address in sorted(converted_instruction.keys()):
        string += "address: {:08X},code: {:08X}".format(address, converted_instruction[address]["machine_code"])
        string += "\n"
    return string


if __name__ == "__main__":
    #import os

    # for folder_name in os.walk("test"):
    #     for filename in folder_name[2]:
    #         clean_code=read_clean_code("test/"+filename)
    #         pass
    clean_code = read_clean_code("8queen.asm")
    converted_instruction = convert_assembly(clean_code)
    nice_print_string = nice_print(converted_instruction)
    pass
