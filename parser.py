#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import itertools
OPCODE_OFFSET=26
RS_OFFSET=21
RT_OFFSET=16
RD_OFFSET=11
SHAMT_OFFSET=6
FUNC_OFFSET=0
IMM_OFFSET=0
RELOCATION={
    "jalr","jr",
    "beq","bgtz","blez","bltz","bne",#TODO:check
    "j","jal"
}
R_OFFSETS=[FUNC_OFFSET,RS_OFFSET,RT_OFFSET,RD_OFFSET,SHAMT_OFFSET]
R_TYPES=["should not appear","register","register","register","shamt"]
R_INSTRUCTIONS={
    #funccode,rs position(in parameters),rt position,rd position, shamt position
    "jalr":[9,0,-1,1,-1],
    "jr":[8,0,-1,-1,-1],
    "slt":[0x2a,1,2,0,-1],
    "xor":[0x26,1,2,0,-1],
    "subu":[0x23,1,2,0,-1],
    "sub":[0x22,1,2,0,-1],
    "srl":[2,-1,1,0,2],
    "sra":[3,-1,1,0,2],
    "sll":[0,-1,1,0,2],
    "or":[0x25,1,2,0,-1],
    "nor":[0x27,1,2,0,-1],
    "and":[0x20,1,2,0,-1],
    "addu":[0x20,1,2,0,-1],
    "add":[0x20,1,2,0,-1]
}
I_INSTRUCTIONS={
    #OPCODE.
    #rs position,rt position,imm position would be 1,0,2
    "addi":8,
    "adddiu":9,
    "andi":0xc,
    "slti":0xa,
    "sltiu":0xb,
    "beq":4,#
    "bgtz":7,#
    "blez":6,#
    "bltz":1,#
    "bne":5#
}
#TODO:注意不同指令地址指定，有的是2开始，有的是0开始，把这个放在哪里实现？
SL_INSTRUCTIONS={
    #OPCODE
    #rs,rt,imm should be -1,0,1
    "lui":0xf,
    "lw":0x23,
    "sw":0x2b
}
J_INSTRUCTIONS={
    #OPCODE
    "j":2,#
    "jal":3,#
}
BJ_MODULUS={
    "beq":16,
    "bgtz":16,
    "blez":16,
    "bltz":16,
    "bne":16,
    "j":26,
    "jal":26
}
def type_instruction(instruction):
    #return param_number,[(param,param_type,param_offset)],(constant,constant_offset)
    immediate_string="immediate"
    if instruction in RELOCATION:
        immediate_string="relocate"
    if instruction in J_INSTRUCTIONS:
        return 0,[],(J_INSTRUCTIONS[instruction],OPCODE_OFFSET)
    elif instruction in SL_INSTRUCTIONS:
        return 2,[(0,"register",RT_OFFSET),(1,immediate_string,IMM_OFFSET)],(SL_INSTRUCTIONS[instruction],OPCODE_OFFSET)
    elif instruction in I_INSTRUCTIONS:
        return 3,[(1,"register",RS_OFFSET),(0,"register",RT_OFFSET),(2,immediate_string,IMM_OFFSET)],(I_INSTRUCTIONS[instruction],OPCODE_OFFSET)

    elif instruction in R_INSTRUCTIONS:
        param_number=max(R_INSTRUCTIONS[instruction][1:])+1
        param_offsets_pair=[(R_INSTRUCTIONS[instruction][i],R_TYPES[i],R_OFFSETS[i]) for i in range(1,len(R_OFFSETS)) if R_INSTRUCTIONS[instruction][i]!=-1]
        return param_number,param_offsets_pair,(R_INSTRUCTIONS[instruction][0],FUNC_OFFSET)
def decode_register():
    pass
def read_clean_code(filename):
    raw_codeline=[]
    with open(filename) as fd:
        raw_codeline=fd.readlines()
    code_without_comma=[]
    for i,line in enumerate(raw_codeline):
        #TODO: supppose string does not exist
        line=line.strip()
        comment_position=-1
        for j in range(len(line)):
            if line[j]=="#":
                comment_position=j
                break
        if comment_position>0:
            code_without_comma.extend(line[0:comment_position].split(","))
        else:
            code_without_comma.extend(line.split(","))
    clean_code=[]
    for i,code_seg in enumerate(code_without_comma):
        clean_code.extend(code_without_comma[i].split())
    return clean_code
TEXT_ADDRESS_START_POSITION=0x00000000
def parse_assembly():
    filename=""
    clean_code = read_clean_code(filename)#得到一个指令list，每个元素为指令/寄存器/立即数
    i=0

    #将指令转换为{address:{"machine_code":machine_code(,"relocation":relocation,"tag":tag)}}
    parsed_instruction = {}
    tag_address={} #tag_name:address
    text_address_relocate=[] #记录了需要重定向的指令的地址
    address = TEXT_ADDRESS_START_POSITION
    while(i<len(clean_code)-1):
        parsed_instruction[address]={}
        if clean_code[i].find(":")!=-1:
            parsed_instruction[address]["tag"]=clean_code[i][0:-1]
            tag_address[clean_code[i][0:-1]]=address
            i+=1
        param_number,param_types_offsets,(constant,constant_offset)=type_instruction(clean_code[i])
        machine_code=constant<<constant_offset
        for param,param_type,param_offset in param_types_offsets:
            if param_type=="immediate" or "shamt":
                machine_code+=int(clean_code[i+param+1])<<param_offset
            elif param_type=="register":
                machine_code+=decode_register(clean_code[i+param+1])<<param_offset
            elif param_type=="relocate":
                parsed_instruction[address]["relocate"]=clean_code[i+param+1]
                parsed_instruction[address]["relocate_type"]=clean_code[i]
            else:
                raise ValueError, "unexpected param_type"
        i+=param_number#寄存器/立即数
        #解析下一条指令
        i+=1
        address+=4

    #对跳转指令进行重定向，注意不同指令的差异：
    #B开头的是[17:2]位，jr,jal也是，TODO:似乎都是？
    for text_address in text_address_relocate:
        destination=tag_address[parsed_instruction[address]["relocate"]]
        parsed_instruction[text_address]["relocate"]=destination
        # 对重定向的地址的机器码加上地址（立即数部分）：
        machine_code_offset= (destination>>2)%BJ_MODULUS[parsed_instruction[text_address]["relocate_type"]]
        parsed_instruction[text_address]["machine_code"]+=machine_code_offset<<0





if __name__=="__main__":
    import os
    for folder_name in os.walk("test"):
        for filename in folder_name[2]:
            clean_code=read_clean_code("test/"+filename)
            pass
