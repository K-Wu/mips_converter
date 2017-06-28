addi $a0,$zero,3  #$a0=3
jal sum           #跳转到sum
Loop:
beq $zero,$zero,Loop
sum:
addi $sp, $sp, -8 #建栈存储$ra,$a0
sw $ra, 4($sp)
sw $a0, 0($sp)
slti $t0, $a0, 1 #如果$a0<1(即$a0减到0)那么$t0赋值为1
beq $t0, $zero, L1 #如果$t0==0那么跳转到L1
xor $v0, $zero, $zero #$v0=0
addi $sp, $sp, 8 #退栈
jr $ra           #跳转回$ra指向地址
L1:
addi $a0, $a0, -1 #$a0=$a0-1
jal sum           #设置$ra为下一条指令，跳转到sum
#上面代码建栈存储了从初始$a0(第0条指令addi设置的常数)到0的各整数
lw $a0, 0($sp)    #读取$a0
lw $ra, 4($sp)    #读取$ra
addi $sp, $sp 8   #退栈
add $v0, $a0, $v0 #$v0+=$a0
jr $ra            #跳转回$ra指向地址

#	    address 	  output     reference
#0addi	0x00000000	0x20040003
#1jal	0x00000004	0x0c100003
#2beq	0x00000008	0x1000ffff   (Loop)
#3addi	0x0000000c	0x23bdfff8   (sum)
#4sw	0x00000010	0xafbf0004
#5sw	0x00000014	0xafa40000
#6slti	0x00000018	0x28880001
#7beq	0x0000001c	0x11000003
#8xor	0x00000020	0x00001026
#9addi	0x00000024	0x23bd0008
#10jr	0x00000028	0x03e00008
#11addi	0x0000002c	0x2084ffff    (L1)
#12jal	0x00000030	0x0c000003
#13lw	0x00000034	0x8fa40000
#14lw	0x00000038	0x8fbf0004
#15addi	0x0000003c	0x23bd0008
#16add	0x00000040	0x00821020
#17jr	0x00000044	0x03e00008
