# MIPS ASSEMBLY CONVERTER
将MIPS汇编语言转换成机器码。并提供一份不完全的机器码转换回汇编语言的代码。

仅支持30+个核心指令，参见相关dict，不支持伪指令

~~靠，边角条件太多了。。。~~

##已知bug：
1. `tag:instruction` 冒号后没有空格时会出问题
2. 不支持`nop`，暂时替代方案：使用`sll $0, $0, 0x0000`替换

## reference:
1. http://logos.cs.uic.edu/366/notes/mips%20quick%20tutorial.htm
2. Computer Organization and Design: The Hardware/Software Interface
3. 17sp Digital Circuits and Computer Design, Department of Electronic Engineering, Tsinghua University