import tables
import math

from PIL import ImageDraw


class CodeGeneration:

    def __init__(self):
        self.__version_number = None
        self.__block_data_amount = None
        self.__blocks_num = None
        self.__image = None
        self.__module_size = None
        self.__modules_number = None
        self.__remainder = None
        self.__DATA_QR = None    
        self.__positions = None    


    def get_version_number(self):
        return self.__version_number
    
    def set_version_number(self, version_number):
        self.__version_number = version_number

    def get_block_data_amount(self):
        return self.__block_data_amount
    
    def set_block_data_amount(self, block_data_amount):
        self.__block_data_amount = block_data_amount

    def get_blocks_num(self):
        return self.__blocks_num
    
    def set_blocks_num(self, blocks_num):
        self.__blocks_num = blocks_num

    def get_image(self):
        return self.__image
    
    def set_image(self, image):
        self.__image = image

    def get_module_size(self):
        return self.__module_size
    
    def set_module_size(self, module_size):
        self.__module_size = module_size

    def get_modules_number(self):
        return self.__modules_number
    
    def set_modules_number(self, modules_number):
        self.__modules_number = modules_number

    def get_remainder(self):
        return self.__remainder
    
    def set_remainder(self, remainder):
        self.__remainder = remainder

    def get_DATA_QR(self):
        return self.__DATA_QR
    
    def set_DATA_QR(self, DATA_QR):
        self.__DATA_QR = DATA_QR

    def get_positions(self):
        return self.__positions
    
    def set_positions(self, positions):
        self.__positions = positions

    
    @staticmethod
    def versionNumber(bit_length):
        i = 1

        while i < len(tables.max_bits):
            if bit_length > int(tables.max_bits[str(i)]):
                i = i + 1
            else:
                return i


    @staticmethod
    def fieldLength(version):
        if version <= 9:
            return tables.ield_length["1-9"]
        elif 10 <= version <= 26:
            return tables.field_length["10-26"]
        else:
            return tables.field_length["27-40"]


    @staticmethod
    def filling(self, bit_sequence: str):
        
        while (len(bit_sequence)) % 8 != 0:
            bit_sequence = bit_sequence + "0"
        
        print(bit_sequence)
        counter = 1

        while len(bit_sequence) != tables.max_bits[str(self.__version_number)]:

            if counter % 2 != 0:
                bit_sequence = bit_sequence + "11101100"
            else:
                bit_sequence = bit_sequence + "00010001"
            counter += 1

        return bit_sequence


    @staticmethod
    def blocksBin2DecTranslation(blocks: list):
        result_blocks = list()

        for i in range(len(blocks)):
            result_blocks.append([])

        for i in range(len(blocks)):
            q = 0
            j = 0

            while j < len(blocks[i]):
                j = q + 8
                result_blocks[i].append((int(blocks[i][q:j], 2)))
                q = j

        return result_blocks


    def binCorrectionCreating(self, bloks: list):
        version_number = self.__version_number
        
        numberBinCorrection = tables.correction_bytes_per_block[str(version_number)]
        polynomial = tables.generating_polynomials[
            str(tables.orrection_bytes_per_block[str(version_number)])
        ]
        listCorrection = []

        for i in range(len(bloks)):
            listCorrection_forNblok = [0] * max(len(bloks[i]), numberBinCorrection)

            for j in range(len(bloks[i])):
                listCorrection_forNblok[j] = bloks[i][j]

            q = 0
            while q < len(listCorrection_forNblok):
                a = listCorrection_forNblok[q]
                listCorrection_forNblok.pop(q)
                listCorrection_forNblok.append("0")

                if int(a) != 0:
                    b = tables.inverse_galoise_fields[str(a)]

                    for k in range(0, numberBinCorrection):
                        c = polynomial[k] + b

                        if c > 254:
                            c = c % 255

                        listCorrection_forNblok[k] = int(
                            int(tables.galois_fields[str(c)]) ^ int(listCorrection_forNblok[k])
                        )
                    q += 1
                else:
                    q += 1
            listCorrection.append(listCorrection_forNblok)

        return listCorrection


    def combiningBlocks(self, bloks: list, correction_bloks):

        blocks_num = self.__blocks_num
        resultList = []
        bin_current = 0

        while bin_current < self.__block_data_amount + 1:
            if bin_current < self.__block_data_amount:
                for blocks_current in range(blocks_num):
                    resultList.append(bloks[blocks_current][bin_current])
            else:
                for bin_current in range(blocks_num - int(self.__remainder), blocks_num):
                    resultList.append(bloks[blocks_current][bin_current])

            bin_current += 1

        bin_current = 0
        while bin_current < tables.correction_bytes_per_block[str(self.__version_number)]:
            for combiningBlocks_current in range(len(correction_bloks)):
                resultList.append(correction_bloks[combiningBlocks_current][bin_current])
            bin_current += 1
        return resultList


    @staticmethod
    def bytesToBits(byte_list):
        bits = "".join(f"{int(byte):08b}" for byte in byte_list)
        return bits


    def moduleSizeCalculation(self):
        SIZE_QRCODE = 300
        pixel_size_per_module = SIZE_QRCODE / (21 + (self.__version_number - 1) * 4)

        while (pixel_size_per_module % 1 != 0) | (math.sqrt(pixel_size_per_module) % 1 != 0):
            SIZE_QRCODE += 1
            pixel_size_per_module = SIZE_QRCODE / (21 + (self.__version_number - 1) * 4)

        print(f"Кол-во пикселей в модуле: {pixel_size_per_module}")
        print(f"Размер QR кода в пикселях: {SIZE_QRCODE}")

        bin_unicode_input = []
        bin_unicode_input.append(SIZE_QRCODE)
        bin_unicode_input.append(pixel_size_per_module)

        print(bin_unicode_input[0])
        return bin_unicode_input
    

    @staticmethod
    def moduleDrawing(self, x, y, color):
            module_size = self.__module_size
            draw = ImageDraw.Draw(self.__image)

            if color == "black":
                color = (0, 0, 0, 255)

            elif color == "white":
                color = (255, 255, 255, 255)

            draw.rectangle(
                [
                    x * module_size,
                    y * module_size,
                    (x + 1) * module_size - 1,
                    (y + 1) * module_size - 1,
                ],
                fill=color,
            )


    def searchPatternGenerating(self):
    # Функция для рисования поискового узора        
        def searchPatternDrawing(x, y, exclude_border):
            drawing = CodeGeneration.moduleDrawing
            
            if exclude_border == "LeftTop":
                for i in range(7):
                    for j in range(7):
                        drawing(x + i, y + j, color="black")
                for i in range(5):
                    for j in range(5):
                        drawing(x + i + 1 , y + j + 1, "white")
                for i in range(3):
                    for j in range(3):
                        drawing(x + i + 2 , y + j + 2 , "black")

                for i in range(7):
                    drawing(7 , i, "white")
                for i in range(8):
                    drawing(i , 7, "white")

            elif exclude_border =="right":

                for i in range(7):
                    for j in range(7):
                        drawing(x - i, y + j, "black")
                for i in range(5):
                    for j in range(5):
                        drawing(x - i - 1, y + j + 1, "white")
                for i in range(3):
                    for j in range(3):
                        drawing(x - i - 2, y + j + 2, "black")

                for i in range(7):
                    drawing(x - 7 , i, "white")   
                for i in range(8):
                    drawing(x - i , 7, "white")

            elif exclude_border =="Left!Top":

                for i in range(7):
                    for j in range(7):
                        drawing(x + i, y - j, "black")
                for i in range(5):
                    for j in range(5):
                        drawing(x + i + 1, y - j - 1, "white")
                for i in range(3):
                    for j in range(3):
                        drawing(x + i + 2, y - j - 2, "black")

                for i in range(7):
                    drawing(7 ,y - i, "white")
                for i in range(8):
                    drawing(i , y - 7, "white")
        
        searchPatternDrawing(0, 0, exclude_border="LeftTop")  # Верхний левый угол


        if self.__modules_number >= 7:
            searchPatternDrawing(self.__modules_number - 1, 0, exclude_border="right")  # Правый верхний угол


        if self.__modules_number >= 7:
            searchPatternDrawing(0, self.__modules_number - 1, exclude_border="Left!Top")  # Левый нижний угол


    @staticmethod
    def isEmptyModule(self, x, y):
        module_size = self.__module_size

        for i in range(x * module_size, (x + 1) * module_size - 1):
            for j in range(y * module_size, (y + 1) * module_size - 1):
                pixel = self.__image.getpixel((i, j))

                if len(pixel) == 4:
                    if pixel[3] != 0:
                        return False
                else:
                    return False

        return True


    @staticmethod
    def alignmentPatternDrawing(self, x, y):
            for i in range(5):
                for j in range(5):
                    CodeGeneration.moduleDrawing(x + i - 2, y + j - 2, color="black")

            for i in range(3):
                for j in range(3):
                    CodeGeneration.moduleDrawing(x - 1 + i, y - 1 + j, "white")

            CodeGeneration.moduleDrawing(x, y, "black")

    def alignmentPatternGenerating(self):
        positions = self.__positions
        # Исключает конфликт с поисковыми узорами для версий больше 6
        if (self.__version_number > 6):
            exclude_positions = {
                (positions[0], positions[0]),
                (positions[0], positions[-1]),
                (positions[-1], positions[0]),
            }
        else:
            exclude_positions = set()

        # Рисует выравнивающие узоры на заданных узлах сетки
        for i in positions:
            for j in positions:
                if (i, j) not in exclude_positions:
                    CodeGeneration.alignmentPatternDrawing(i, j)

    @staticmethod
    def isInAlignmentPattern(self, x, y):
        for ax in self.__positions:
            for ay in self.__positions:
                # Пропускает узоры, которые пересекаются с поисковыми (верхний левый, верхний правый и нижний левый)
                if (ax == 6 and (ay == 6 or ay == self.__modules_number - 7)) \
                or (ay == 6 and ax == self.__modules_number - 7):
                    continue

                # Находится ли точка внутри выравнивающего узора?
                if ax - 2 <= x <= ax + 2 and ay - 2 <= y <= ay + 2:
                    return True

        return False

    def syncBandsGenerating(self):
        x = 8
        y = 6
        stripe_color = "black"

        while x < self.__modules_number - 7:

            if not CodeGeneration.isInAlignmentPattern(x, y):
                CodeGeneration.moduleDrawing(x, y, stripe_color)

            if stripe_color == "black":
                stripe_color = "white"

            else:
                stripe_color = "black"
            x += 1
        x = 6
        y = 8
        stripe_color = "black"

        while y < self.__modules_number - 7:

            if not CodeGeneration.isInAlignmentPattern(x, y):
                CodeGeneration.moduleDrawing(x, y, stripe_color)

            if stripe_color == "black":
                stripe_color = "white"

            else:
                stripe_color = "black"
            y += 1

    def codeVersionDrawing(version_code, offset_x, offset_y):

        for i in range(len(version_code)):
            color = "black" if version_code[i] == "1" else "white"

            if i < 6:
                CodeGeneration.moduleDrawing(offset_x, offset_y + i, color)
                CodeGeneration.moduleDrawing(offset_y + i, offset_x, color)

            elif 6 <= i < 12:
                CodeGeneration.moduleDrawing(offset_x + 1, offset_y + i - 6, color)
                CodeGeneration.moduleDrawing(offset_y + i - 6, offset_x + 1, color)

            else:
                CodeGeneration.moduleDrawing(offset_x + 2, offset_y + i - 12, color)
                CodeGeneration.moduleDrawing(offset_y + i - 12, offset_x + 2, color)

    
    @staticmethod
    def masking(x, y, color):
        mask_3 = (x + y) % 3

        if mask_3 == 0:
            if color == "white":
                color = "black"
            else:
                color = "white"

        return color

    def maskCodeAndCorrectionLevel(self):
        code = "111100010011101"
        color = "black"
        j = 0

        CodeGeneration.moduleDrawing(8, self.__modules_number - 8, color)

        for i in range(7):

            if code[i] == 0:
                color = "white"
            else:
                color = "black"
            CodeGeneration.moduleDrawing(8, self.__modules_number - 1 - i, color)

            if j == 6:
                j += 1

            CodeGeneration.moduleDrawing(j, 8, color)
            j += 1

        j = 0

        for i in range(7, len(code)):

            if code[i] == 0:
                color = "white"
            else:
                color = "black"
            CodeGeneration.moduleDrawing(self.__modules_number - 8 + i - 7, 8, color)

            if j == 2:
                j += 1
            CodeGeneration.moduleDrawing(8, 8 - j, color)
            j += 1

    def QRDataFilling(self):
        color: str
        data_index = 0

        for col in range(self.__modules_number - 1, -1, -2):
            # В пределах одного столбика чередуем движение: снизу вверх, сверху вниз
            for row in range(self.__modules_number - 1, -1, -1):
                for x_offset in range(2):
                    x = col - x_offset
                    y = row
                    # Если модуль свободен, заполняем его данными
                    if CodeGeneration.isEmptyModule(x, y):
                        if data_index < len(self.__DATA_QR):

                            if int(self.__DATA_QR[data_index]) == 0:
                                color = "white"
                            else:
                                color = "black"
                            color = CodeGeneration.masking(x, y, color)
                            CodeGeneration.moduleDrawing(x, y, color)
                            data_index += 1

                        else:
                            color = "white"
                            color = CodeGeneration.masking(x, y, color)
                            CodeGeneration.moduleDrawing(x, y, color)  # Если данные закончились, заполняем 0
            # Двигаемся вверх
            for row in range(self.__modules_number):
                for x_offset in range(2):
                    x = col - x_offset
                    y = row

                    if CodeGeneration.isEmptyModule(x, y):
                        if data_index < len(self.__DATA_QR):
                            if int(self.__DATA_QR[data_index]) == 0:
                                color = "white"
                            else:
                                color = "black"
                            color = CodeGeneration.masking(x, y, color)
                            CodeGeneration.moduleDrawing(x, y, color)
                            data_index += 1
                        else:
                            color = "white"
                            color = CodeGeneration.masking(x, y, color)
                            CodeGeneration.moduleDrawing(x, y, color)