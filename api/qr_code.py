import ast
import math

from PIL import Image

from PIL import Image, ImageDraw, ImageOps

inputInformation = "!Kapibara !!! 0_0 Kapibara !!! 0_0 Kapibara !!! 0_0" 
result = []
result = ''.join(format(ord(x), '08b') for x in inputInformation)
lenData = len(result)
lendataBit = []
lendataBit.append(str(bin(lenData)[2:]))

lenDataBin = lenData/8
print("строка в двоичном коде:")
print(result)
print("Длина строки")
print(lenData)
print("длина строки в двоичном коде:")
print(lendataBit)

Table2M_Maxi_amount_information = {
    '1':128, '2':224, '3':352, '4':512, '5':688, 
    '6':864, '7':992, '8':1232, '9':1456, '10':1728,
    '11':2032, '12':2320, '13':2672, '14':2920, '15':3320, 
    '16':3624, '17':4056, '18':4504, '19':5016, '20':5352,
    '21':5712, '22':6256, '23':6880, '24':7312, '25':800, 
    '26':8496, '27':9024, '28':9544, '29':10136, '30': 10984,
    '31':11640, '32':12328, '33':13048, '34':13800, '35':14496,
    '36':15312, '37':15936, '38': 16816, '39':17728, '40':18672
}

def numberVersion(lenBit):
    i = 1   
    while i < len(Table2M_Maxi_amount_information ):
        if(lenBit > int(Table2M_Maxi_amount_information [str(i)])):
            i = i+1
        else:
            return i
VERSION_NUMBER = numberVersion(lenData)    
print('версия')
print(numberVersion(lenData))


Table3_Length_data_quantity_field = {
    '1-9':8, '10-26':16, '27-40':16
}
 
def lenField(version):
    if version <= 9:
        return Table3_Length_data_quantity_field ['1-9']
    elif 10 <= version <= 26:
        return Table3_Length_data_quantity_field ['10-26']
    else:
        return Table3_Length_data_quantity_field ['27-40']
print("длина поля")
print(lenField(VERSION_NUMBER))

res = []
res = '0'+'1'+'0'+'0'+lendataBit[0] + result
print("Результат после указание типа кодирование и длины входной строкии")
print(res)

Table4M_Number_of_blocks = {
    '1':1, '2':1, '3':1, '4':2, '5':2, 
    '6':4, '7':4, '8':4, '9':5, '10':5, 
    '11':5, '12':8, '13':9, '14':9, '15':10, 
    '16':10, '17':11, '18':13, '19':14, '20':16,
    '21': 17, '22':17, '23':18, '24':20, '25':21, 
    '26':23, '27':25, '28':26, '29':28, '30':29, 
    '31':31, '32':33, '33':35, '34':37, '35':38, 
    '36':40, '37':43, '38':45, '39':47, '40':49
}

def filling(bitSequence: str):
    while (len(bitSequence)) %8 != 0:
        bitSequence= bitSequence+'0'
    print(bitSequence)
    counter = 1
    while len(bitSequence) != Table2M_Maxi_amount_information[str(VERSION_NUMBER)]:
        if counter%2 != 0:
           bitSequence= bitSequence +'11101100'
        else:
            bitSequence = bitSequence + '00010001'
        counter +=1
    return bitSequence

res = filling(res)
print("Результат после заполнения")
print(res)
print("Длина после заполнения")
print(len(res))

NUMBER_BLOCK = Table4M_Number_of_blocks[str(VERSION_NUMBER)]
print("кол-во блоков")
print(NUMBER_BLOCK)

amountDataInBlock =  (len(res)/8)//NUMBER_BLOCK
print("кол-во данных в блоке")
print(amountDataInBlock)

remainder = (len(res)/8)%NUMBER_BLOCK
print("Остаток")
print(remainder)

bloks = []
q = 0
j = amountDataInBlock*8
for i in range(0,int(NUMBER_BLOCK-remainder)):
    bloks.append(res[int(q):int(j)])
    q = amountDataInBlock*8
    j = j + amountDataInBlock*8

if remainder!=0:
    q = amountDataInBlock*8 +8
    for i in range(0,int(remainder)):
        bloks.append(res[int(j):int(q)])
        j = amountDataInBlock*8+8
        q = q+amountDataInBlock*8+8

for i in range(len(bloks)):
    print(bloks[i])


print(res)

print('Длинна первого блока')
print(len(bloks[0]))

Table5M_Number_CorrectionBytes_per_block = {
    '1':10, '2':16, '3':26, '4':18, '5':24, 
    '6':16, '7':18, '8':22, '9':22, '10':26, 
    '11':30, '12':22, '13':22, '14':24, '15':24, 
    '16':28, '17':28, '18':26, '19':26, '20':26,
    '21': 26, '22':28, '23':28, '24':28, '25':28, 
    '26':28, '27':28, '28':28, '29':28, '30':28, 
    '31':28, '32':28, '33':28, '34':28, '35':28, 
    '36':28, '37':28, '38':28, '39':28, '40':28
}

Table6_Generating_polynomials={
    '10':[251, 67, 46, 61, 118, 70, 64, 94, 32, 45],
    '16':[120, 104, 107, 109, 102, 161, 76, 3, 91, 191,
          147, 169, 182, 194, 225, 120],
    '18':[215, 234, 158, 94, 184, 97, 118, 170, 79, 187, 
          152, 148, 252, 179, 5, 98, 96, 153],
    '22':[210, 171, 247, 242, 93, 230, 14, 109, 221, 53, 
          200, 74, 8, 172, 98, 80, 219, 134, 160, 105, 165, 231],
    '24':[229, 121, 135, 48, 211, 117, 251, 126, 159, 
          180, 169, 152, 192, 226, 228, 218, 111, 0, 117, 232, 87, 96, 227, 21],
    '26':[173, 125, 158, 2, 103, 182, 118, 17, 145, 201,
           111, 28, 165, 53, 161, 21, 245, 142, 13, 102, 48, 227, 153, 145, 218, 70],
    '28':[168, 223, 200, 104, 224, 234, 108, 180, 110, 190,
           195, 147, 205, 27, 232, 201, 21, 43, 245, 87, 42, 195, 212, 119, 242, 37, 9, 123],
    '30':[41, 173, 145, 152, 216, 31, 179, 182, 50, 48, 110,
           86, 239, 96, 222, 125, 42, 173, 226, 193, 224, 130, 156, 37, 251, 216, 238, 40, 192, 180]
}


print("Полином")
polynomial = Table6_Generating_polynomials[str(Table5M_Number_CorrectionBytes_per_block[str(VERSION_NUMBER)])]
print(polynomial)
print(polynomial[0])


def bloks_translation_from_2_to_10(bloks: list):
    resultBloks = list()
    for i in range(len(bloks)):
        resultBloks.append([])
    for i in range(len(bloks)):
         q = 0
         j = 0
         while j<len(bloks[i]):
             j = q+8
             resultBloks[i].append((int(bloks[i][q:j],2)))
             q = j
    
    return resultBloks

bloks = bloks_translation_from_2_to_10(bloks)

print("Блоки в 10тичной системе")
for i in range(len(bloks)):
    print(bloks[i]) 

print("Длина первого блока:" + str(len(bloks[0])))
print("Длина второго блока:" + str(len(bloks[1])))

print(bloks[0][1])
Table7_Galois_field={
'0': 1, '1': 2, '2': 4, '3': 8, '4': 16, '5': 32, '6': 64, '7': 128, '8': 29, '9': 58, '10': 116,
'11': 132, '12': 205, '13': 135, '14': 19, '15': 38, '16': 76, '17': 152, '18': 45, '19': 90, '20': 180,
'21': 117, '22': 234, '23': 201, '24': 143, '25': 3, '26': 6, '27': 12, '28': 24, '29': 48, '30': 96,
'31': 192, '32': 157, '33': 39, '34': 78, '35': 156, '36': 37, '37': 74, '38': 148, '39': 53, '40': 106,
'41': 212, '42': 181, '43': 119, '44': 238, '45': 193, '46': 159, '47': 35, '48': 70, '49': 140, '50': 5,
'51': 10, '52': 20, '53': 40, '54': 80, '55': 160, '56': 93, '57': 186, '58': 105, '59': 210, '60': 185,
'61': 111, '62': 222, '63': 161, '64': 95, '65': 190, '66': 97, '67': 194, '68': 153, '69': 47, '70': 94,
'71': 188, '72': 101, '73': 202, '74': 137, '75': 15, '76': 30, '77': 60, '78': 120, '79': 240, '80': 253,
'81': 231, '82': 211, '83': 187, '84': 107, '85': 214, '86': 177, '87': 127, '88': 254, '89': 225, '90': 223,
'91': 163, '92': 91, '93': 182, '94': 113, '95': 226, '96': 217, '97': 175, '98': 67, '99': 134, '100': 17,
'101': 34, '102': 68, '103': 136, '104': 13, '105': 26, '106': 52, '107': 104, '108': 208, '109': 189,'110': 103,
'111': 206, '112': 129, '113': 31, '114': 62, '115': 124, '116': 248, '117': 137, '118': 199,'119': 147, 
'120': 59,'121':118,'122':236,'123':197,'124':151,'125':51,'126':102,'127':204,'128':133,'129':23,
'130':46,'131':92,'132':184,'133':109,'134':218,'135':169 ,'136':79 ,'137':158 ,'138':33 ,'139':66,
'140':132 ,'141':21 ,'142':42 ,'143':84 ,'144':168 ,'145':77 ,'146':154 ,'147':41 ,'148':82 ,'149':164,
'150':85 ,'151':170 ,'152':73 ,'153':146 ,'154':57 ,'155':114 ,'156':228 ,'157':213 ,'158':183 ,
'159':115 ,'160':230 ,'161':209 ,'162':191 ,'163':99 ,'164':198 ,'165':145 ,'166':63 ,'167':126 ,
'168':252 ,'169':229 ,'170':215 ,'171':179 ,'172':123 ,'173':246 ,'174':241 ,'175':255 ,'176':227 ,
'177':219 ,'178':171 ,'179':75 ,'180':150 ,'181':49 ,'182':98 ,'183':196 ,'184':149 ,'185':55 ,
'186':110 ,'187':220 ,'188':165 ,'189':87 ,'190':174 ,'191':65 ,'192':130 ,'193':25 ,'194':50 ,
'195':100 ,'196':200 ,'197':141 ,'198':7 ,'199':14 ,'200':28 , '201':56 ,'202':112 ,'203':224 ,'204':221 ,
'205':167 ,'206':83 ,'207':166 ,'208':81 ,'209':162 ,'210':89 , '211':178 ,'212':121 ,'213':242 ,'214':249 ,
'215':239 ,'216':195 ,'217':155 ,'218':43 ,'219':86 ,'220':172 ,'221':69 ,'222':138 ,'223':9 ,'224':18 ,'225':36 ,
'226':72 ,'227':144 ,'228':61 ,'229':122 ,'230':245 , '231':245 , '232':247 , '233':243 , '234':251 , 
'235':235 , '236':203 , '237':139 , '238':11 , '239':22 , '240':44 , '241':88 , '242':176 , '243':125 , '244':250 , 
'245':233 ,'246':207 , '247':131 , '248':27 , '249':54 , '250':108 , '251':216 , '252':173 , '253':71 , '254':142 , '255':1 
}


Table8_Inverse_Galois_field={
'1': 0, '2': 1, '3': 25, '4': 2, '5': 50, '6': 26, '7': 198, '8': 3, '9': 223, '10': 51, 
'11': 238, '12': 27, '13': 104, '14': 199, '15': 75, '16': 4, '17': 100, '18': 224, '19': 14, '20': 52, 
'21': 141, '22': 239, '23': 129, '24': 28, '25': 193, '26': 105, '27': 248, '28': 200, '29': 8, '30': 76, 
'31': 113, '32': 5, '33': 138, '34': 101, '35': 47, '36': 225, '37': 36, '38': 15, '39': 33, '40': 53, 
'41': 147, '42': 142, '43': 218, '44': 240, '45': 18, '46': 130, '47': 69, '48': 29, '49': 181, '50': 194, 
'51': 125, '52': 106, '53': 39, '54': 249, '55': 185, '56': 201, '57': 154, '58': 9, '59': 120, '60': 77, 
'61': 228, '62': 114, '63': 166, '64': 6, '65': 191, '66': 139, '67': 98, '68': 102, '69': 221, '70': 48, 
'71': 253, '72': 226, '73': 152, '74': 37, '75': 179, '76': 16, '77': 145, '78': 34, '79': 136, '80': 54,
'81': 208, '82': 148, '83': 206, '84': 143, '85': 150, '86': 219, '87': 189, '88': 241, '89': 210, '90': 19,
'91': 92, '92': 131, '93': 56, '94': 70, '95': 64, '96': 30, '97': 66, '98': 182, '99': 163, '100': 195,
'101': 72, '102': 126, '103': 110, '104': 107, '105': 58, '106': 40, '107': 84, '108': 250, '109': 133,
'110': 186,'111':61,'112':202,'113':94,'114':15,'115':159,'116':10,'117':21,'118':121,'119':43,
'120':78,'121':212,'122':229,'123':172,'124':115,'125':243,'126':167,'127':87,'128':7,'129':112,
'130':192,'131':247,'132':140,'133':128,'134':99,'135':13,'136':103,'137':74,'138':222,'139':237,
'140':49,'141':197,'142':254,'143':24,'144':227,'145':165,'146':153,'147':119,'148':38,'149':184,
'150':180,'151':124,'152':17,'153':68,'154':146,'155':217,'156':35, '157':32,'158':137,'159':46,
'160':55,'161':63,'162':209,'163':91,'164':149,'165':188,'166':207,'167':205,'168':144,'169':135,
'170':151,'171':178,'172':220,'173':252,'174':190,'175':97,'176':242,'177':86,'178':211,'179':171,
'180':20,'181':42,'182':93,'183':158,'184':132,'185':60,'186':57,'187':83,'188':71,'189':109,
'190':65,'191':162,'192':31,'193':45,'194':67,'195':216,'196':183,'197':123,'198':164,'199':118,
'200':196 ,'201':23 ,'202':73 ,'203':236 ,'204':127 ,'205':12 ,'206':111 ,'207':246 ,'208':108 ,
'209':161 ,'210':59 ,'211':82 ,'212':41 ,'213':157 ,'214':85 ,'215':170 ,'216':251 ,'217':96 ,
'218':134 ,'219':177 ,'220':187 ,'221':204 ,'222':62 ,'223':90 ,'224':203 ,'225':89 ,'226':95 ,
'227':176 ,'228':156 ,'229':169 ,'230' :160 ,'231' :81 ,'232' :11 ,'233' :245 ,'234' :22 ,'235' :235 ,
'236':122 ,'237' :117 ,'238' :44 ,'239' :215 ,'240' :79 ,'241' :174 ,'242' :213 ,'243' :233 ,'244' :230 ,
'245':231 ,'246' :173 ,'247' :232 ,'248' :116 ,'249' :214 , '250' :244 , '251' :234 , '252' :168 , '253' :80 , 
'254':88 , '255' :175

}
def create_Bin_correction(bloks: list):

    numberBinCorrection = Table5M_Number_CorrectionBytes_per_block[str(VERSION_NUMBER)]
    polynomial = Table6_Generating_polynomials[str(Table5M_Number_CorrectionBytes_per_block[str(VERSION_NUMBER)])]
    listCorrection = [] 
    for i in range(len(bloks)):
        
        listCorrection_forNblok = [0]*max(len(bloks[i]),numberBinCorrection)
        for j in range(len(bloks[i])):
            listCorrection_forNblok[j] = bloks[i][j]

        q=0
        while q < len(listCorrection_forNblok):
            a = listCorrection_forNblok[q]
            listCorrection_forNblok.pop(q)
            listCorrection_forNblok.append('0')
            if(int(a) != 0): 
                b = Table8_Inverse_Galois_field[str(a)]
                for k in range(0,numberBinCorrection):
                    c = polynomial[k] + b
                    if(c>254):
                        c = c%255
                    listCorrection_forNblok[k]= int(int(Table7_Galois_field[str(c)]) ^ int(listCorrection_forNblok[k]))
                q+=1
            else:
                q+=1
        listCorrection.append(listCorrection_forNblok)
    return listCorrection
print("Байты коррекции")
print(create_Bin_correction(bloks))

def combining_blocks(bloks: list, correction_bloks ):
     
    resultList = []
    bin_current = 0 

    while bin_current < amountDataInBlock+1:
        if(bin_current < amountDataInBlock):
            for blocks_current in range (NUMBER_BLOCK):
                resultList.append(bloks[blocks_current][bin_current])
        else:
            for bin_current in range(NUMBER_BLOCK-int(remainder), NUMBER_BLOCK):
                 resultList.append(bloks[blocks_current][bin_current])

        bin_current+=1

    bin_current = 0
    while bin_current < Table5M_Number_CorrectionBytes_per_block[str(VERSION_NUMBER)]:
        for combining_blocks_current in range (len(correction_bloks)):
            resultList.append(correction_bloks[combining_blocks_current][bin_current])
        bin_current+=1
    return resultList

print("Объедененные блоки")
#print(combining_blocks(bloks,create_Bin_correction(bloks)))

DATA_QR = combining_blocks(bloks,create_Bin_correction(bloks))
print(DATA_QR)

def bytes_to_bits(byte_list):
    """
    Преобразует список байтов в строку битов.
    """
    bits = ''.join(f'{int(byte):08b}' for byte in byte_list)
    return bits
DATA_QR = bytes_to_bits(combining_blocks(bloks,create_Bin_correction(bloks)))
print(bytes_to_bits(combining_blocks(bloks,create_Bin_correction(bloks))))







def calculating_size_image_and_module():

    SIZE_QRCODE = 300
    size_pixle_in_module = SIZE_QRCODE / (21 + (VERSION_NUMBER - 1)*4)


    while((size_pixle_in_module%1 != 0) | (math.sqrt(size_pixle_in_module)%1 != 0)):
        SIZE_QRCODE += 1
        size_pixle_in_module = SIZE_QRCODE / (21 + (VERSION_NUMBER - 1)*4)
    
    print("Кол-во пикселей в модуле")
    print(size_pixle_in_module)

    print("Размер QR кода в пикселях")
    print(SIZE_QRCODE)

    result = []
    result.append(SIZE_QRCODE)
    result.append(size_pixle_in_module)

    print(result[0])
    return(result)


# Рассчитываем размер стороны модуля в пикселях
module_size = int(calculating_size_image_and_module()[0]/ (21 + (VERSION_NUMBER - 1)*4))

# Количество модулей по горизонтали и вертикали
num_modules = (21 + (VERSION_NUMBER - 1)*4)


image = Image.new("RGBA", (calculating_size_image_and_module()[0], calculating_size_image_and_module()[0]), (256, 256, 256, 0))
draw = ImageDraw.Draw(image)


# Функция для рисования модуля
def draw_module(x, y, color):
    if color == 'black':
        color = (0, 0, 0, 255)  # Черный с указанной прозрачностью
    elif color == 'white':
        color = (255, 255, 255, 255)  # Белый с указанной прозрачностью

    draw.rectangle(
        [x * module_size, y * module_size, (x + 1) * module_size - 1, (y + 1) * module_size - 1],
        fill=color, 
    )

def generate_qr_search_pattern():
    # Функция для рисования поискового узора
    def draw_finder_pattern(x, y, exclude_border):
    
        if exclude_border == "LeftTop":
            for i in range(7):
                for j in range(7):
                    draw_module(x + i, y + j, "black")
            for i in range(5):
                for j in range(5):
                    draw_module(x + i + 1 , y + j + 1, "white")
            for i in range(3):
                for j in range(3):
                    draw_module(x + i + 2 , y + j + 2 , "black")

            for i in range(7):
                draw_module(7 , i, "white")
            for i in range(8):
                draw_module(i , 7, "white")

        elif exclude_border =="right":

            for i in range(7):
                for j in range(7):
                    draw_module(x - i, y + j, "black")
            for i in range(5):
                for j in range(5):
                    draw_module(x - i - 1, y + j + 1, "white")
            for i in range(3):
                for j in range(3):
                    draw_module(x - i - 2, y + j + 2, "black")

            for i in range(7):
                draw_module(x - 7 , i, "white")   
            for i in range(8):
                draw_module(x - i , 7, "white")

        elif exclude_border =="Left!Top":

            for i in range(7):
                for j in range(7):
                    draw_module(x + i, y - j, "black")
            for i in range(5):
                for j in range(5):
                    draw_module(x + i + 1, y - j - 1, "white")
            for i in range(3):
                for j in range(3):
                    draw_module(x + i + 2, y - j - 2, "black")

            for i in range(7):
                draw_module(7 ,y - i, "white")
            for i in range(8):
                draw_module(i , y - 7, "white")



    draw_finder_pattern(0, 0, exclude_border="LeftTop")  # Верхний левый угол


    if num_modules >= 7:
        draw_finder_pattern(num_modules - 1, 0, exclude_border="right")  # Правый верхний угол


    if num_modules >= 7:
        draw_finder_pattern(0, num_modules - 1, exclude_border="Left!Top")  # Левый нижний угол


Table_9_alignment_pattern= {
    2:[18], 3:[22], 4:[26], 5:[30], 
    6:[34], 7:[6, 22, 38], 8:[6, 24, 42], 9:[6, 26, 46], 10:[6, 28, 50], 
    11:[6, 30, 54], 12:[6, 32, 58], 13:[6, 34, 62], 14:[6, 26, 46, 66], 15:[6, 26, 48, 70], 
    16:[6, 26, 50, 74], 17:[6, 30, 54, 78], 18:[6, 30, 56, 82], 19:[6, 30, 58, 86], 20:[6, 34, 62, 90],
    21:[6, 28, 50, 72, 94], 22:[6, 26, 50, 74, 98], 23:[6, 30, 54, 78, 102], 24:[6, 28, 54, 80, 106],
    25:[6, 32, 58, 84, 110], 26:[6, 30, 58, 86, 114], 27:[6, 34, 62, 90, 118], 28:[6, 26, 50, 74, 98, 122], 
    29:[6, 30, 54, 78, 102, 126], 30:[6, 26, 52, 78, 104, 130], 31:[6, 30, 56, 82, 108, 134], 
    32:[6, 34, 60, 86, 112, 138], 33:[6, 30, 58, 86, 114, 142], 34:[6, 34, 62, 90, 118, 146], 
    35:[6, 30, 54, 78, 102, 126, 150], 36:[6, 24, 50, 76, 102, 128, 154], 37:[6, 28, 54, 80, 106, 132, 158], 
    38:[6, 32, 58, 84, 110, 136, 162], 39:[6, 26, 54, 82, 110, 138, 166], 40:[6, 30, 58, 86, 114, 142, 170]
}

positions = Table_9_alignment_pattern[VERSION_NUMBER]

def check_empty_modele(x, y):
    for i in range(x * module_size, (x + 1) * module_size - 1):
        for j in range(y * module_size, (y + 1) * module_size - 1):
            # Получаем цвет пикселя
            pixel = image.getpixel((i, j))
            # Проверяем, есть ли у изображения альфа-канал
            if len(pixel) == 4: 
                # Если хотя бы один пиксель не прозрачен
                if pixel[3] != 0:
                    return False
            else:
                # Если у изображения нет альфа-канала, оно не может быть прозрачным
                return False
    
    return True


def generate_qr_alignment_pattern():

    #выравнивающий узор 5x5 с центром в точке (x, y).
    def draw_alignment_pattern(x, y):
    # Наружная черная рамка 5x5
        for i in range(5):
            for j in range(5):
                draw_module(x + i - 2, y + j - 2, "black")
    # Внутренняя белая рамка 3x3
        for i in range(3):
            for j in range(3):
                draw_module(x - 1 + i , y - 1 + j, "white")        
    # Центральный черный модуль 1x1
        draw_module(x, y, "black")

    #координаты центров выравнивающих узоров
    positions = Table_9_alignment_pattern[VERSION_NUMBER]

    # Исключает конфликт с поисковыми узорами для версий больше 6
    if VERSION_NUMBER > 6:
         exclude_positions = {(positions[0], positions[0]), (positions[0], positions[-1]), (positions[-1], positions[0])}
    else:
        exclude_positions = set()

    # Рисует выравнивающие узоры на заданных узлах сетки
    for i in positions:
        for j in positions:
            if (i, j) not in exclude_positions:
                draw_alignment_pattern(i, j)

def is_in_alignment_pattern(x, y):

    for ax in positions:
        for ay in positions:
            # Пропускает узоры, которые пересекаются с поисковыми (верхний левый, верхний правый и нижний левый)
            if (ax == 6 and (ay == 6 or ay == num_modules - 7)) or (ay == 6 and ax == num_modules - 7):
                    continue

            # Находится ли точка внутри выравнивающего узора?
            if ax - 2 <= x <= ax + 2 and ay - 2 <= y <= ay + 2:
                return True
    return False
    
def generate_sync_bands():

    x = 8
    y = 6
    stripe_color = 'black'
    while x < num_modules - 7 :
        if not is_in_alignment_pattern(x, y):
            draw_module(x, y, stripe_color)
        if stripe_color == 'black':
            stripe_color = 'white'
        else: 
            stripe_color = 'black'
        x += 1
        
    x = 6
    y = 8
    stripe_color = 'black'
    while y < num_modules - 7 :
        if not is_in_alignment_pattern(x, y):
            draw_module(x, y, stripe_color)
        if stripe_color == 'black':
            stripe_color = 'white'
        else: 
            stripe_color = 'black'
        y += 1

TAble10_version_codes = {
    7: "000010011110100110",
    8: "010001011100111000",
    9: "110111011000000100",
    10: "101001111110000000",
    11: "001111111010111100",
    12: "001101100100011010",
    13: "101011100000100110",
    14: "110101000110100010",
    15: "010011000010011110",
    16: "011100010001011100",
    17: "111010010101100000",
    18: "100100110011100100",
    19: "000010110111011000",
    20: "000000101001111110",
    21: "100110101101000010",
    22: "111000001011000110",
    23: "011110001111111010",
    24: "001101001101100100",
    25: "101011001001011000",
    26: "110101101111011100",
    27: "010011101011100000",
    28: "010001110101000110",
    29: "110111110001111010",
    30: "101001010111111110",
    31: "001111010011000010",
    32: "101000011000101101",
    33: "001110011100010001",
    34: "010000111010010101",
    35: "110110111110101001",
    36: "110100100000001111",
    37: "010010100100110011",
    38: "001100000010110111",
    39: "101010000110001011",
    40: "111001000100010101"
}

def draw_version_code(version_code, offset_x, offset_y):

    for i in range(len(version_code)):
        color = 'black' if version_code[i] == '1' else 'white'
        if (i < 6):
            draw_module(offset_x, offset_y + i, color)
            draw_module(offset_y + i, offset_x, color)
        elif(6 <= i < 12):
            draw_module(offset_x+1, offset_y + i - 6, color)
            draw_module(offset_y + i - 6, offset_x + 1, color)
        else:
            draw_module(offset_x+2, offset_y + i - 12, color)
            draw_module(offset_y + i - 12, offset_x + 2, color)

# Пример вызова функции
generate_qr_search_pattern()
generate_qr_alignment_pattern()
generate_sync_bands()
if VERSION_NUMBER >=7:
   draw_version_code(TAble10_version_codes[VERSION_NUMBER], num_modules - 11, 0)

def masking(x, y, color):
    mask_3 = (x + y)%3
    if(mask_3 == 0):
        if(color == 'white'):
            color = 'black'
        else:
            color = 'white'
    return color

def mask_code_and_correction_level():

    code = '111100010011101'
    color = 'black'
    j = 0
    draw_module(8,num_modules - 8, color)
    for i in range(7):

        if code[i] == '0':
            color = 'white'
        else:
            color = 'black'
        draw_module(8,num_modules - 1 - i, color)

        if j == 6:
            j += 1  

        draw_module(j, 8, color)
        j += 1 

    j = 0
    for i in range(7,len(code)):

        if code[i] == '0':
            color = 'white'
        else:
            color = 'black'
        draw_module(num_modules - 8 + i - 7,8, color)    

        if j == 2:
            j += 1 
        draw_module(8, 8 - j, color)
        j += 1 
        

def fill_qr_data():
    color: str
    data_index = 0
    for col in range(num_modules - 1, -1, -2):    
        #В пределах одного столбика чередуем движение: снизу вверх, сверху вниз
        for row in range(num_modules - 1, -1, -1):
            for x_offset in range(2):
                x = col - x_offset
                y = row
                #Если модуль свободен, заполняем его данными
                if check_empty_modele(x, y):
                    if data_index < len(DATA_QR):
                        
                        if int(DATA_QR[data_index]) == 0:
                            color = 'white'
                        else:
                            color = 'black'
                        color = masking(x, y, color)
                        draw_module(x, y, color)
                        data_index += 1

                    else:
                        color = 'white'
                        color = masking(x,y,color)
                        draw_module(x,y, color) # Если данные закончились, заполняем 0
        #Двигаемся вверх
        for row in range(num_modules):
            for x_offset in range(2):
                x = col - x_offset
                y = row

                if check_empty_modele(x, y):
                    if data_index < len(DATA_QR):
                        if int(DATA_QR[data_index]) == 0:
                            color = 'white'
                        else:
                            color = 'black'
                        color = masking(x,y,color)
                        draw_module(x,y, color)
                        data_index += 1
                    else:
                        color = 'white'
                        color = masking(x,y,color)
                        draw_module(x,y, color) 

mask_code_and_correction_level()
fill_qr_data()

# Сохраняем изображение
image = ImageOps.expand(image, border=module_size, fill='white')

image.save("finder_pattern.png")
image.show()