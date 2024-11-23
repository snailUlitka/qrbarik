import tables
import math

from PIL import Image
from PIL import ImageDraw


class CodeGeneration:

    def __init__(self, version_number):
        self.__version_number = version_number

    @property
    def version_number(self):
        return self.__version_number
    
    @version_number.setter
    def version_number(self, value):
        self.__version_number = value

    @version_number.deleter
    def version_number(self):
        del self.__version_number
    

    @staticmethod
    def define_version(bit_length: int) -> int:
        i = 1

        while i < len(tables.MAX_BITS):
            if bit_length > tables.MAX_BITS[i]:
                i += 1
            else:
                return i
        return i

    @staticmethod
    def field_length(version: int) -> int:
        if version <= 9:
            return tables.FIELD_LENGTH["1-9"]
        elif 10 <= version <= 26:
            return tables.FIELD_LENGTH["10-26"]
        return tables.FIELD_LENGTH["27-40"]

    @classmethod
    def service_fields(cls, input: str) -> tuple[int, str]:
        bin_unicode_input = "".join(
            format(ord(ch), "08b") for ch in input
        )
        byte_unicode_length = len(input)
        version_number = cls.define_version(len(bin_unicode_input))
        unicode_len_without_prefix = format(
            byte_unicode_length, "08b" if version_number < 10 else "016b"
        )
        res = f"0100{unicode_len_without_prefix}{bin_unicode_input}"

        if len(res) > tables.MAX_BITS[version_number]:
            while len(res) > tables.MAX_BITS[version_number]:
                version_number += 1
                unicode_len_without_prefix = format(
                    byte_unicode_length, "08b" if version_number < 10 else "016b"
                )
                res = f"0100{unicode_len_without_prefix}{bin_unicode_input}"

        res = cls.bit_seq_null_filling(
            version_number, res
        )

        return (version_number, res)

    @staticmethod
    def bit_seq_null_filling(version_number: int, bit_sequence: str) -> str:

        while (len(bit_sequence)) % 8 != 0:
            bit_sequence += "0"

        counter = 1

        while len(bit_sequence) != tables.MAX_BITS[version_number]:

            if counter % 2 != 0:
                bit_sequence += "11101100"
            
            else:
                bit_sequence += "00010001"
            counter += 1

        return bit_sequence

    def bin_blocks_filling(self, res: str) -> tuple[list[str], int, int]:
        binary_blocks: list[str] = []
        
        blocks_num = tables.BLOCKS_NUMBER[self.version_number]
        bytes_amount = len(res) // 8
        data_per_block = bytes_amount // blocks_num
        remain = bytes_amount % blocks_num
        
        q = 0
        j = data_per_block * 8

        for i in range(blocks_num - remain):

            binary_blocks.append(res[q:j])
            q = j
            j += data_per_block * 8

        if remain != 0:
            q = data_per_block * (blocks_num - remain) * 8
            j += 8

            for i in range(remain):
                binary_blocks.append(res[q:j])
                q = j
                j += data_per_block * 8 + 8

        return binary_blocks, remain, data_per_block

    @staticmethod
    def blocks_bin2dec_translation(blocks: list[str]) -> list[list[int]]:
        result_blocks: list = list()

        for i in range(len(blocks)):
            result_blocks.append([])

        for i in range(len(blocks)):
            q, j = 0, 0

            while j < len(blocks[i]):
                q = j
                j += 8
                result_blocks[i].append(int(blocks[i][q:j], 2))

        return result_blocks

    def bin_correction_creating(self, blocks: list[list[int]]) -> list[list[int]]:
        if self.version_number is not None:

            bin_correction_number = tables.CORRECTION_BYTES_PER_BLOCK[self.version_number]
            polynomial = tables.GENERATING_POLYNOMIALS[bin_correction_number]
            list_correction: list = []

            for i in range(len(blocks)):
                list_correction_for_block: list = [0] * max(
                    len(blocks[i]), bin_correction_number
                )

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

                list_correction.append(list_correction_for_block)

        return list_correction

    def blocks_combination(
        self,
        blocks: list[list[int]],
        correction_blocks: list[list[int]],
        remainder,
        data_per_block,
    ) -> list[int]:
        blocks_num = tables.BLOCKS_NUMBER[self.version_number]
        result_list: list[int] = []

        current_byte = 0
        
        while (current_byte <= data_per_block):
            if current_byte < data_per_block:
                for current_block in range(blocks_num):
                    result_list.append(blocks[current_block][current_byte])
            else:
                for current_block in range(blocks_num - remainder, blocks_num):
                    result_list.append(blocks[current_block][current_byte])
            current_byte += 1
        
        current_byte = 0
        bytes_per_block = tables.CORRECTION_BYTES_PER_BLOCK[self.version_number]
        
        while (current_byte < bytes_per_block):
            for current_comb_block in range(len(correction_blocks)):
                result_list.append(
                    correction_blocks[current_comb_block][current_byte]
                )
            current_byte += 1

        return result_list

    @staticmethod
    def bytes2bits(byte_list: list[str]) -> str:
        bits = "".join(f"{int(byte):08b}" for byte in byte_list)
        return bits

    def module_size_calculation(self, qr_code_size=300):
        if self.version_number is not None:
            pixels_num_per_module = qr_code_size / (
                21 + (self.version_number - 1) * 4
            )

            while (pixels_num_per_module % 1 != 0) | (
                math.sqrt(pixels_num_per_module) % 1 != 0
            ):
                qr_code_size += 1
                pixels_num_per_module = int(
                    qr_code_size / (21 + (self.version_number - 1) * 4)
                )

            return qr_code_size, pixels_num_per_module

    @staticmethod
    def module_drawing(
        module_size: int, image: Image.Image, x: int, y: int, color: str
    ) -> None:
        if image is not None:
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

    def get_modules_number(self) -> int:
        return 21 + (self.version_number - 1) * 4

    def search_pattern_generation(self, image: Image.Image) -> None:
        module_size = self.module_size_calculation()[1]
        modules_number = self.get_modules_number()

        def search_pattern_drawing(x: int, y: int, exclude_border: str) -> None:
            drawing = self.module_drawing
            
            if exclude_border == "TopLeft":
                for i in range(7):
                    for j in range(7):
                        drawing(module_size, image, x + i, y + j, color="black")
                for i in range(5):
                    for j in range(5):
                        drawing(module_size, image, x + i + 1, y + j + 1, "white")
                for i in range(3):
                    for j in range(3):
                        drawing(module_size, image, x + i + 2, y + j + 2, "black")
                for i in range(7):
                    drawing(module_size, image, 7, i, "white")
                for i in range(8):
                    drawing(module_size, image, i, 7, "white")
            
            elif exclude_border == "TopRight":
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
                    drawing(module_size, image, x - 7, i, "white")
                for i in range(8):
                    drawing(module_size, image, x - i, 7, "white")
            
            elif exclude_border == "BottomLeft":
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
                    drawing(module_size, image, 7, y - i, "white")
                for i in range(8):
                    drawing(module_size, image, i, y - 7, "white")

        search_pattern_drawing(0, 0, exclude_border="TopLeft")
        
        if modules_number >= 7:
            search_pattern_drawing(modules_number - 1, 0, exclude_border="TopRight")
            search_pattern_drawing(0, modules_number - 1, exclude_border="BottomLeft")

    @staticmethod
    def is_empty_module(module_size: int, image: Image.Image, x: int, y: int) -> bool:
        if module_size is not None:
            for i in range(x * module_size, (x + 1) * module_size - 1):
                for j in range(y * module_size, (y + 1) * module_size - 1):
                    pixel = image.getpixel((i, j))

                    if isinstance(pixel, tuple) and len(pixel) == 4:
                        if pixel[3] != 0:
                            return False
        return True

    @classmethod
    def alignment_pattern_drawing(
        cls, module_size: int, image: Image.Image, x: int, y: int
    ) -> None:
        for i in range(5):
            for j in range(5):
                cls.module_drawing(
                    module_size, 
                    image, 
                    x + i - 2, 
                    y + j - 2, 
                    color="black"
                )

        for i in range(3):
            for j in range(3):
                cls.module_drawing(module_size, image, x - 1 + i, y - 1 + j, "white")

        cls.module_drawing(module_size, image, x, y, "black")

    def alignment_pattern_generation(self, image: Image.Image) -> None:
        module_size = self.module_size_calculation()[1]
        positions = tables.ALIGNMENT_PATTERN[self.version_number]
        # Исключает конфликт с поисковыми узорами для версий больше 6
        if self.version_number > 6:
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
                    self.alignment_pattern_drawing(module_size, image, i, j)

    def is_in_alignment_pattern(self, x: int, y: int) -> bool:
        modules_number = self.get_modules_number()

        if self.version_number == 1:
            return False

        positions = tables.ALIGNMENT_PATTERN[self.version_number]

        for ax in positions:
            for ay in positions:
                # Пропускает узоры, которые пересекаются с поисковыми (верхний левый, верхний правый и нижний левый)
                if (ax == 6 and (ay == 6 or ay == modules_number - 7)) or (
                    ay == 6 and ax == modules_number - 7
                ):
                    continue
                # Находится ли точка внутри выравнивающего узора?
                if ax - 2 <= x <= ax + 2 and (ay - 2 <= y <= ay + 2):
                    return True
        return False

    def sync_bands_generation(self, image: Image.Image) -> None:
        modules_number = self.get_modules_number()
        module_size = self.module_size_calculation()[1]
        x = 8
        y = 6
        stripe_color = "black"

        while x < modules_number - 7:

            if not self.is_in_alignment_pattern(x, y):
                self.module_drawing(module_size, image, x, y, stripe_color)

            if stripe_color == "black":
                stripe_color = "white"

            else:
                stripe_color = "black"
            x += 1
        
        x = 6
        y = 8
        stripe_color = "black"

        while y < modules_number - 7:

            if not self.is_in_alignment_pattern(x, y):
                self.module_drawing(module_size, image, x, y, stripe_color)

            if stripe_color == "black":
                stripe_color = "white"

            else:
                stripe_color = "black"
            y += 1

    def code_version_drawing(
        self, offset_x: int, offset_y: int, image: Image.Image
    ) -> None:
        module_size = self.module_size_calculation()[1]
        version_code = tables.VERSION_CODES[self.version_number]

        for i in range(len(version_code)):
            color = "black" if version_code[i] == "1" else "white"

            if i < 6:
                self.module_drawing(module_size, image, offset_x, offset_y + i, color)
                self.module_drawing(module_size, image, offset_y + i, offset_x, color)

            elif 6 <= i < 12:
                self.module_drawing(
                    module_size, image, offset_x + 1, offset_y + i - 6, color
                )
                self.module_drawing(
                    module_size, image, offset_y + i - 6, offset_x + 1, color
                )

            else:
                self.module_drawing(
                    module_size, image, offset_x + 2, offset_y + i - 12, color
                )
                self.module_drawing(
                    module_size, image, offset_y + i - 12, offset_x + 2, color
                )

    @staticmethod
    def masking(x: int, y: int, color: str) -> str:
        mask_3 = (x + y) % 3

        if mask_3 == 0:
            if color == "white":
                color = "black"
            else:
                color = "white"
        return color

    def mask_code_and_correction_level(self, image: Image.Image) -> None:
        module_size = self.module_size_calculation()[1]
        modules_number = self.get_modules_number()
        code = "111100010011101"
        color = "black"
        j = 0

        self.module_drawing(module_size, image, 8, modules_number - 8, color)

        for i in range(7):

            if code[i] == 0:
                color = "white"
            else:
                color = "black"
            self.module_drawing(module_size, image, 8, modules_number - 1 - i, color)

            if j == 6:
                j += 1

            self.module_drawing(module_size, image, j, 8, color)
            j += 1

        j = 0

        for i in range(7, len(code)):

            if code[i] == 0:
                color = "white"
            else:
                color = "black"
            
            self.module_drawing(
                module_size, image, modules_number - 8 + i - 7, 8, color
            )

            if j == 2:
                j += 1
            
            self.module_drawing(module_size, image, 8, 8 - j, color)
            j += 1

    def qr_data_filling(self, image: Image.Image, qr_data) -> None:
        module_size = self.module_size_calculation()[1]
        modules_number = self.get_modules_number()
        data_index = 0

        for col in range(modules_number - 1, -1, -2):
            # В пределах одного столбика чередуем движение: снизу вверх, сверху вниз
            for row in range(modules_number - 1, -1, -1):
                for x_offset in range(2):
                    x = col - x_offset
                    y = row
                    # Если модуль свободен, заполняем его данными
                    if self.is_empty_module(module_size, image, x, y):
                        if data_index < len(qr_data):

                            if int(qr_data[data_index]) == 0:
                                color = "white"
                            else:
                                color = "black"
                            color = self.masking(x, y, color)
                            self.module_drawing(module_size, image, x, y, color)
                            data_index += 1

                        else:
                            color = "white"
                            color = self.masking(x, y, color)
                            self.module_drawing(
                                module_size, image, x, y, color
                            )  # Если данные закончились, заполняем 0
            # Двигаемся вверх
            for row in range(modules_number):
                for x_offset in range(2):
                    x = col - x_offset
                    y = row

                    if self.is_empty_module(module_size, image, x, y):
                        if data_index < len(qr_data):
                            if int(qr_data[data_index]) == 0:
                                color = "white"
                            else:
                                color = "black"
                            color = self.masking(x, y, color)
                            self.module_drawing(module_size, image, x, y, color)
                            data_index += 1
                        else:
                            color = "white"
                            color = self.masking(x, y, color)
                            self.module_drawing(module_size, image, x, y, color)
