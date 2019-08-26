from dec2bin import *

def decoder(data):

    def binaryToDecimal(binary):
        binary1 = binary
        decimal, i, n = 0, 0, 0
        while (binary != 0):
            dec = binary % 10
            decimal = decimal + dec * pow(2, i)
            binary = binary // 10
            i += 1
        return decimal
    if data == "00":
        while len(data) != 8:
            data = '0' + data
    size = len(data)
    reg1_object = slice(5)
    reg2_object = slice(5, 6 + (size - 5) - 1)
    reg1 = int(data[reg1_object])
    reg2 = int(data[reg2_object])
    j9 = int(reg1 / 256)
    j10 = dec2bin(j9)
    while len(j10) != 8:
        j10 = '0' + j10
    j13_object = slice(1)
    j13 = j10[j13_object]
    if int(j13) == 0:
        j14 = 1
    else:
        j14 = -1

    m9 = reg2 - int(reg2 / 256) * 256
    m10 = dec2bin(m9)
    while len(m10) != 8:
        m10 = '0' + m10

    l9 = int(reg2 / 256)
    l10 = dec2bin(l9)
    while len(l10) != 8:
        l10 = '0' + l10

    k9 = reg1 - int(reg1 / 256) * 256
    k10 = dec2bin(k9)
    while len(k10) != 8:
        k10 = '0' + k10
    k10_copy = k10

    k10_object = slice(1, len(k10))
    k10 = k10[k10_object]
    k10 = int(k10)
    k10 = binaryToDecimal(k10)
    l10 = binaryToDecimal(int(l10))
    m10 = binaryToDecimal(int(m10))
    n15 = k10 * 256 * 256 + l10 * 256 + m10
    n16 = 8388608
    n17 = n15 / n16 + 1
    o16 = 4194304
    o15 = n15
    o17 = o15 / o16

    j18_object = slice(1, len(j10))
    k10_object = slice(1)
    j18 = j10[j18_object] + k10_copy[k10_object]
    j19 = binaryToDecimal(int(j18))

    n21 = n17 if j19 > 0 else o17

    k19 = j19 - 127
    answer = j14 * n21 * 2 ** k19
    return answer

