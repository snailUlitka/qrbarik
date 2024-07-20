
inputInformation = "!Kapibara !!! 0_0" 
result = []
result = ''.join(format(ord(x), '08b') for x in inputInformation)

lenData = len(result)
lendataBit = []
lendataBit.append(str(bin(lenData)[2:]))

lenDataBin = lenData/8

print(result)
print(lenData)
print(lendataBit)

Tabl2M ={
    '1':128, '2':224, '3':352, '4':512, '5':688, '6':864, '7':992, '8':1232, '9':1456, '10':1728,
    '11':2032, '12':2320, '13':2672, '14':2920, '15':3320, '16':3624, '17':4056, '18':4504, '19':5016, '20':5352,
    '21':5712, '22':6256, '23':6880, '24':7312, '25':800, '26':8496, '27':9024, '28':9544, '29':10136, '30': 10984,
    '31':11640, '32':12328, '33':13048, '34':13800, '35':14496, '36':15312, '37':15936, '38': 16816, '39':17728, '40':18672
}

def numberVersion(lenBit):
    i=1   
    while i < len(Tabl2M):
        if(lenBit > int(Tabl2M[str(i)])):
            i = i+1
        else:
            return i
print(numberVersion(lenData))
ver  = numberVersion(lenData)
Tabl3 = {
    '1-9':8, '10-26':16, '27-40':16
}
 
def lenField(version):
    if version <= 9:
        return Tabl3['1-9']
    elif 10<=version <=26:
        return Tabl3['10-26']
    else:
        return Tabl3['27-40']
print(lenField(ver))

res = []
res = '0'+'1'+'0'+'0'+lendataBit[0] + result
print(res)
