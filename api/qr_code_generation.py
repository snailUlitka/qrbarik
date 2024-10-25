import tables
import math

from PIL import Image
from PIL import ImageDraw


class CodeGeneration:

    def __init__(self, version_number, modules_number, positions, 
                 version_code, blocks_num, remainder, block_data_amount):
        self.__version_number = version_number
        self.__modules_number = modules_number
        self.__positions = positions 
        self.__version_code = version_code    
        self.__blocks_num = blocks_num
        self.__remainder = remainder
        self.__block_data_amount = block_data_amount
        self.__image = None
        self.__module_size = None
        self.__DATA_QR = None    

    def get_version_number(self):
        return self.__version_number
    
    def set_version_number(self, version_number):
        self.__version_number = version_number

    version = property(get_version_number, set_version_number)

    def get_block_data_amount(self):
        return self.__block_data_amount
    
    def set_block_data_amount(self, block_data_amount):
        self.__block_data_amount = block_data_amount

    block_data_amount = property(get_block_data_amount, set_block_data_amount)

    def get_blocks_num(self):
        return self.__blocks_num
    
    def set_blocks_num(self, blocks_num):
        self.__blocks_num = blocks_num

    blocks_num = property(get_blocks_num, set_blocks_num)

    def get_image(self):
        return self.__image
    
    def set_image(self, image):
        self.__image = image

    image = property(get_image, set_image)

    def get_module_size(self):
        return self.__module_size
    
    def set_module_size(self, module_size):
        self.__module_size = module_size

    module_size = property(get_module_size, set_module_size)

    def get_modules_number(self):
        return self.__modules_number
    
    def set_modules_number(self, modules_number):
        self.__modules_number = modules_number

    modules_number = property(get_modules_number, set_modules_number)

    def get_remainder(self):
        return self.__remainder
    
    def set_remainder(self, remainder):
        self.__remainder = remainder

    remainder = property(get_remainder, set_remainder)

    def get_DATA_QR(self):
        return self.__DATA_QR
    
    def set_DATA_QR(self, DATA_QR):
        self.__DATA_QR = DATA_QR

    DATA_QR = property(get_DATA_QR, set_DATA_QR)

    def get_positions(self):
        return self.__positions
    
    def set_positions(self, positions):
        self.__positions = positions

    positions = property(get_positions, set_positions)

    def get_version_code(self):
        return self.__version_code
    
    def set_version_code(self, version_code):
        self.__version_code = version_code

    version_code = property(get_version_code, set_version_code)

    
    @staticmethod
    def define_version(bit_length: int):
        i = 1
        while i < len(tables.MAX_BITS):
            if bit_length > tables.MAX_BITS[i]:
                i = i + 1
            else:
                return i
        return None
        

    @staticmethod
    def field_length(version: int) -> int:
        if version <= 9:
            return tables.FIELD_LENGTH["1-9"]
        elif 10 <= version <= 26:
            return tables.FIELD_LENGTH["10-26"]
        return tables.FIELD_LENGTH["27-40"]


    @staticmethod
    def filling(version_number: int, bit_sequence: str) -> str:
        
        while (len(bit_sequence)) % 8 != 0:
            bit_sequence = bit_sequence + "0"
        
        print(bit_sequence)
        counter = 1

        while len(bit_sequence) != tables.MAX_BITS[version_number]:

            if counter % 2 != 0:
                bit_sequence = bit_sequence + "11101100"
            else:
                bit_sequence = bit_sequence + "00010001"
            counter += 1

        return bit_sequence


    @staticmethod
    def blocks_bin2dec_translation(blocks: list[str]) -> list[list[int]]:
        result_blocks: list = list()

        for i in range(len(blocks)):
            result_blocks.append([])

        for i in range(len(blocks)):
            q = 0
            j = 0

            while j < len(blocks[i]):
                j = q + 8
                result_blocks[i].append(int(blocks[i][q:j], 2))
                q = j

        return result_blocks


    def bin_correction_creating(self, blocks: list[list[int]]) -> list[list[int]]:
        if self.version != None:
            version_number = self.version
        
            bin_correction_number = tables.CORRECTION_BYTES_PER_BLOCK[version_number]
            polynomial = tables.GENERATING_POLYNOMIALS[
                tables.CORRECTION_BYTES_PER_BLOCK[version_number]
            ]
            list_correction: list = []

            for i in range(len(blocks)):
                list_correction_for_block: list = [0] * max(len(blocks[i]), bin_correction_number)

                for j in range(len(blocks[i])):
                    list_correction_for_block[j] = blocks[i][j]

                q = 0
                while q < len(list_correction_for_block):
                    a = list_correction_for_block[q]
                    list_correction_for_block.pop(q)
                    list_correction_for_block.append(0)

                    if int(a) != 0:
                        b = tables.INVERSE_GALOISE_FIELDS[a]

                        for k in range(bin_correction_number):
                            c = polynomial[k] + b

                            if c > 254:
                                c = c % 255

                            list_correction_for_block[k] = int(
                                int(tables.GALOISE_FIELDS[c])
                                ^ int(list_correction_for_block[k])
                            )
                        q += 1
                    else:
                        q += 1
                list_correction.append(list_correction_for_block)

        return list_correction


    def blocks_combination(self, blocks: list[list[int]], correction_bloks: list[list[int]]) -> list[int]:
        if self.blocks_num != None and (
            self.block_data_amount != None and (
                self.remainder != None and (
                    self.version != None
                )
            )
        ):
            blocks_num = self.blocks_num
            result_list: list[int] = []
            bin_current = 0

            while bin_current < self.block_data_amount + 1:
                if bin_current < self.block_data_amount:

                    for blocks_current in range(blocks_num - 1):
                        #if blocks[blocks_current][bin_current] != None:
                            result_list.append(blocks[blocks_current][bin_current])
                else:

                    for bin_current in range(
                        blocks_num - int(self.remainder), 
                        blocks_num
                    ):
                        result_list.append(blocks[blocks_current][bin_current])

                bin_current += 1

            bin_current = 0
            bytes_per_block = tables.CORRECTION_BYTES_PER_BLOCK[self.version]

            while bin_current < bytes_per_block:

                for blocks_combination_current in range(
                    len(correction_bloks)
                ):
                    result_list.append(correction_bloks[blocks_combination_current][bin_current])

                bin_current += 1

        return result_list


    @staticmethod
    def bytes2bits(byte_list: list[str]) -> str:
        bits = "".join(
            f"{int(byte):08b}" for byte in byte_list
        )
        return bits


    def module_size_calculation(self):
        if self.version != None:
            SIZE_QRCODE = 300
            pixel_size_per_module = SIZE_QRCODE / (21 + (self.version - 1) * 4)

            while (
                (pixel_size_per_module % 1 != 0) 
                | (math.sqrt(pixel_size_per_module) % 1 != 0)
            ):
                SIZE_QRCODE += 1
                pixel_size_per_module = SIZE_QRCODE / (21 + (self.version - 1) * 4)

            print(f"Кол-во пикселей в модуле: {pixel_size_per_module}")
            print(f"Размер QR кода в пикселях: {SIZE_QRCODE}")

            bin_unicode_input = []
            bin_unicode_input.append(SIZE_QRCODE)
            bin_unicode_input.append(pixel_size_per_module)

            print(bin_unicode_input[0])
            return bin_unicode_input
    

    @staticmethod
    def module_drawing(module_size: int, image: Image.Image, x: int, y: int, color: str) -> None:
        if image != None:
            draw = ImageDraw.Draw(image)

            if color == "black":
                color_channel = (0, 0, 0, 255)

            elif color == "white":
                color_channel = (255, 255, 255, 255)

            draw.rectangle(
                [
                    x * module_size,
                    y * module_size,
                    (x + 1) * module_size - 1,
                    (y + 1) * module_size - 1,
                ],
                fill=color_channel,
            )


    def search_pattern_generating(self) -> None:
    # Функция для рисования поискового узора        
        if self.module_size != None and (
            self.image != None
        ):
            module_size = self.module_size
            image = self.image

            def search_pattern_drawing(x: int, y: int, exclude_border: str) -> None:
                drawing = CodeGeneration.module_drawing

                if exclude_border == "LeftTop":
                    for i in range(7):
                        for j in range(7):
                            drawing(module_size, image, x + i, y + j, color="black")
                    for i in range(5):
                        for j in range(5):
                            drawing(module_size, image, x + i + 1 , y + j + 1, "white")
                    for i in range(3):
                        for j in range(3):
                            drawing(module_size, image, x + i + 2 , y + j + 2 , "black")

                    for i in range(7):
                        drawing(module_size, image, 7 , i, "white")
                    for i in range(8):
                        drawing(module_size, image, i , 7, "white")

                elif exclude_border == "right":

                    for i in range(7):
                        for j in range(7):
                            drawing(module_size, image, x - i, y + j, "black")
                    for i in range(5):
                        for j in range(5):
                            drawing(module_size, image, x - i - 1, y + j + 1, "white")
                    for i in range(3):
                        for j in range(3):
                            drawing(module_size, image, x - i - 2, y + j + 2, "black")

                    for i in range(7):
                        drawing(module_size, image, x - 7 , i, "white")   
                    for i in range(8):
                        drawing(module_size, image, x - i , 7, "white")

                elif exclude_border =="Left!Top":

                    for i in range(7):
                        for j in range(7):
                            drawing(module_size, image, x + i, y - j, "black")
                    for i in range(5):
                        for j in range(5):
                            drawing(module_size, image, x + i + 1, y - j - 1, "white")
                    for i in range(3):
                        for j in range(3):
                            drawing(module_size, image, x + i + 2, y - j - 2, "black")

                    for i in range(7):
                        drawing(module_size, image, 7 ,y - i, "white")
                    for i in range(8):
                        drawing(module_size, image, i , y - 7, "white")

            search_pattern_drawing(0, 0, exclude_border="LeftTop")  # Верхний левый угол


            if self.modules_number >= 7:
                search_pattern_drawing(self.modules_number - 1, 0, exclude_border="right")  # Правый верхний угол


            if self.modules_number >= 7:
                search_pattern_drawing(0, self.modules_number - 1, exclude_border="Left!Top")  # Левый нижний угол


    @staticmethod
    def is_empty_module(module_size: int, image: Image.Image, x: int, y: int) -> bool:
        if module_size != None:
            for i in range(
                x * module_size, 
                (x + 1) * module_size - 1
            ):
                for j in range(
                    y * module_size,
                    (y + 1) * module_size - 1
                ):
                    pixel = image.getpixel((i, j))

                    if isinstance(pixel, tuple) and len(pixel) == 4:
                        if pixel[3] != 0:
                            return False

        return True


    @staticmethod
    def alignment_pattern_drawing(module_size: int, image: Image.Image, x: int, y: int) -> None:
            for i in range(5):
                for j in range(5):
                    CodeGeneration.module_drawing(module_size, image, x + i - 2, y + j - 2, color="black")

            for i in range(3):
                for j in range(3):
                    CodeGeneration.module_drawing(module_size, image, x - 1 + i, y - 1 + j, "white")

            CodeGeneration.module_drawing(module_size, image, x, y, "black")

    def alignment_pattern_generation(self) -> None:
        if self.positions != None:
            positions = self.positions
            # Исключает конфликт с поисковыми узорами для версий больше 6
            if self.version > 6:
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
                        CodeGeneration.alignment_pattern_drawing(self.module_size, self.image, i, j)

    
    def is_in_alignment_pattern(self, x: int, y: int) -> bool:
        if self.positions != None:
            for ax in self.positions:
                for ay in self.positions:
                    # Пропускает узоры, которые пересекаются с поисковыми (верхний левый, верхний правый и нижний левый)
                    if (ax == 6 and (
                        ay == 6 or ay == self.modules_number - 7
                    )) or (ay == 6 and ax == self.modules_number - 7):
                        continue

                    # Находится ли точка внутри выравнивающего узора?
                    if ax - 2 <= x <= ax + 2 and (
                        ay - 2 <= y <= ay + 2
                    ):
                        return True

        return False

    def sync_bands_generation(self) -> None:
        module_size = self.module_size
        image = self.image
        x = 8
        y = 6
        stripe_color = "black"

        while x < self.modules_number - 7:

            if not CodeGeneration.is_in_alignment_pattern(self, x, y):
                CodeGeneration.module_drawing(module_size, image, x, y, stripe_color)

            if stripe_color == "black":
                stripe_color = "white"

            else:
                stripe_color = "black"
            x += 1
        x = 6
        y = 8
        stripe_color = "black"

        while y < self.modules_number - 7:

            if not CodeGeneration.is_in_alignment_pattern(self, x, y):
                CodeGeneration.module_drawing(module_size, image, x, y, stripe_color)

            if stripe_color == "black":
                stripe_color = "white"

            else:
                stripe_color = "black"
            y += 1

    def code_version_drawing(self, version_code: str, offset_x: int, offset_y: int) -> None:

        for i in range(len(version_code)):
            color = "black" if version_code[i] == "1" else "white"

            if i < 6:
                CodeGeneration.module_drawing(self.module_size, self.image, offset_x, offset_y + i, color)
                CodeGeneration.module_drawing(self.module_size, self.image, offset_y + i, offset_x, color)

            elif 6 <= i < 12:
                CodeGeneration.module_drawing(self.module_size, self.image, offset_x + 1, offset_y + i - 6, color)
                CodeGeneration.module_drawing(self.module_size, self.image, offset_y + i - 6, offset_x + 1, color)

            else:
                CodeGeneration.module_drawing(self.module_size, self.image, offset_x + 2, offset_y + i - 12, color)
                CodeGeneration.module_drawing(self.module_size, self.image, offset_y + i - 12, offset_x + 2, color)

    
    @staticmethod
    def masking(x: int, y: int, color: str) -> str:
        mask_3 = (x + y) % 3

        if mask_3 == 0:
            if color == "white":
                color = "black"
            else:
                color = "white"

        return color

    def mask_code_and_correction_level(self) -> None:
        code = "111100010011101"
        color = "black"
        j = 0

        CodeGeneration.module_drawing(self.module_size, self.image, 8, self.modules_number - 8, color)

        for i in range(7):

            if code[i] == 0:
                color = "white"
            else:
                color = "black"
            CodeGeneration.module_drawing(self.module_size, self.image, 8, self.modules_number - 1 - i, color)

            if j == 6:
                j += 1

            CodeGeneration.module_drawing(self.module_size, self.image, j, 8, color)
            j += 1

        j = 0

        for i in range(7, len(code)):

            if code[i] == 0:
                color = "white"
            else:
                color = "black"
            CodeGeneration.module_drawing(self.module_size, self.image, self.modules_number - 8 + i - 7, 8, color)

            if j == 2:
                j += 1
            CodeGeneration.module_drawing(self.module_size, self.image, 8, 8 - j, color)
            j += 1

    def qr_data_filling(self) -> None:
        color: str
        data_index = 0

        for col in range(self.modules_number - 1, -1, -2):
            # В пределах одного столбика чередуем движение: снизу вверх, сверху вниз
            for row in range(self.modules_number - 1, -1, -1):
                for x_offset in range(2):
                    x = col - x_offset
                    y = row
                    # Если модуль свободен, заполняем его данными
                    if CodeGeneration.is_empty_module(self.module_size, self.image, x, y):
                        if data_index < len(self.__DATA_QR):

                            if int(self.__DATA_QR[data_index]) == 0:
                                color = "white"
                            else:
                                color = "black"
                            color = CodeGeneration.masking(x, y, color)
                            CodeGeneration.module_drawing(self.module_size, self.image, x, y, color)
                            data_index += 1

                        else:
                            color = "white"
                            color = CodeGeneration.masking(x, y, color)
                            CodeGeneration.module_drawing(self.module_size, self.image, x, y, color)  # Если данные закончились, заполняем 0
            # Двигаемся вверх
            for row in range(self.modules_number):
                for x_offset in range(2):
                    x = col - x_offset
                    y = row

                    if CodeGeneration.is_empty_module(self.module_size, self.image, x, y):
                        if data_index < len(self.DATA_QR):
                            if int(self.__DATA_QR[data_index]) == 0:
                                color = "white"
                            else:
                                color = "black"
                            color = CodeGeneration.masking(x, y, color)
                            CodeGeneration.module_drawing(self.module_size, self.image, x, y, color)
                            data_index += 1
                        else:
                            color = "white"
                            color = CodeGeneration.masking(x, y, color)
                            CodeGeneration.module_drawing(self.module_size, self.image, x, y, color)