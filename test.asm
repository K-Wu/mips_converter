addi $a0, $zero, 12345 
addiu $a1, $zero, -11215 
sll $a2, $a1, 16 
sra $a3, $a2, 16 
beq $a3, $a1, L1 
lui $a0, 11111 
L1: add $t0, $a2, $a0 
sra $t1, $t0, 8 
addi $t2, $zero, -12345 
slt $v0, $a0, $t2 
sltu $v1, $a0, $t2 
Loop: j Loop
                          output    reference
#address: 00000000,code: 20043039
#address: 00000004,code: 2404D431 xx 2405d431 1.取反时没有取绝对值
#address: 00000008,code: 00053400
#address: 0000000C,code: 00063C03
#address: 00000010,code: 10A70000 xx 10e50001 1.修复relocate（第二遍循环）被跳过的bug后还是不对，变成了xx 10A70006 2.发现b应该调换rs rt位置后变成10e50006 3.发现和PC+4比较后修复
#address: 00000014,code: 3C042B67
#address: 00000018,code: 00C44020 L1
#address: 0000001C,code: 00084A03
#address: 00000020,code: 2009CFC7 xx 200acfc7 1.取反时没有取绝对值
#address: 00000024,code: 008A102A
#address: 00000028,code: 008A182B
#address: 0000002C,code: 08000000 xx 08000000 1.修复relocate（第二遍循环）被跳过的bug后解决。 Loop
