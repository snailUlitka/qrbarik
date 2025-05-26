import tables

from enums import Color, Border
from PIL import ImageDraw
from PIL import Image, ImageOps


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

    @staticmethod
    def service_fields(input: str) -> tuple[int, str]:
        bin_unicode_input = "".join(
            format(ord(ch), "08b") for ch in input
        )
        version_number = CodeGeneration.define_version(len(bin_unicode_input))
        unicode_len_without_prefix = format(
            len(input), "08b" if version_number < 10 else "016b"
        )
        res = f"0100{unicode_len_without_prefix}{bin_unicode_input}"

        if len(res) > tables.MAX_BITS[version_number]:
            while len(res) > tables.MAX_BITS[version_number]:
                version_number += 1
                unicode_len_without_prefix = format(
                    len(input), "08b" if version_number < 10 else "016b"
                )
                res = f"0100{unicode_len_without_prefix}{bin_unicode_input}"

        res = CodeGeneration.bit_seq_null_filling(
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

    def fill_blocks(self, bit_sequence: str) -> tuple[list[str], int, int]:
        binary_blocks: list[str] = []
        
        blocks_num = tables.BLOCKS_NUMBER[self.version_number]
        bytes_amount = len(bit_sequence) // 8
        bytes_per_block = bytes_amount // blocks_num
        remainder_bytes = bytes_amount % blocks_num
        
        q = 0
        j = bytes_per_block * 8

        for _ in range(blocks_num - remainder_bytes):
            binary_blocks.append(bit_sequence[q:j])
            q = j
            j += bytes_per_block * 8

        if remainder_bytes != 0:
            q = bytes_per_block * (blocks_num - remainder_bytes) * 8
            j += 8

            for _ in range(remainder_bytes):
                binary_blocks.append(bit_sequence[q:j])
                q = j
                j += bytes_per_block * 8 + 8

        return binary_blocks, remainder_bytes, bytes_per_block

    @staticmethod
    def translate_blocks_to_dec(bin_blocks: list[str]) -> list[list[int]]:
        result_blocks: list = []

        for i in range(len(bin_blocks)):
            decimal_block = []

            q, j = 0, 0

            while j < len(bin_blocks[i]):
                q = j
                j += 8

                decimal_block.append(int(bin_blocks[i][q:j], 2))
            result_blocks.append(decimal_block)

        return result_blocks

    def create_error_correction(self, blocks: list[list[int]]) -> list[list[int]]:
        bin_correction_number = tables.CORRECTION_BYTES_PER_BLOCK[self.version_number]
        polynomial = tables.GENERATING_POLYNOMIALS[bin_correction_number]
        correction_list: list = []
        
        for i in range(len(blocks)):
            list_correction_for_block: list[int] = [0] * max(
                len(blocks[i]), bin_correction_number
            )
            for j in range(len(blocks[i])):
                list_correction_for_block[j] = blocks[i][j]
            q = 0
            
            while q < len(list_correction_for_block):
                correction_item = list_correction_for_block[q]
                list_correction_for_block.pop(q)
                list_correction_for_block.append(0)
                
                if correction_item != 0:
                    b = tables.INVERSE_GALOISE_FIELDS[correction_item]
                    
                    for k in range(bin_correction_number):
                        c = polynomial[k] + b
                        
                        if c > 254:
                            c = c % 255
                        list_correction_for_block[k] = int(
                            int(tables.GALOISE_FIELDS[c])
                            ^ int(list_correction_for_block[k])
                        )
                q += 1
            correction_list.append(list_correction_for_block)
        return correction_list

    def combinate_blocks(
        self,
        blocks: list[list[int]],
        correction_blocks: list[list[int]],
        remainder,
        bytes_per_block,
    ) -> list[int]:
        blocks_num = tables.BLOCKS_NUMBER[self.version_number]
        result_list: list[int] = []

        current_byte = 0
        
        while (current_byte <= bytes_per_block):
            if current_byte < bytes_per_block:
                for block in range(blocks_num):
                    result_list.append(blocks[block][current_byte])
            else:
                for block in range(blocks_num - remainder, blocks_num):
                    result_list.append(blocks[block][current_byte])

            current_byte += 1
        
        current_byte = 0
        bytes_per_block = tables.CORRECTION_BYTES_PER_BLOCK[self.version_number]
        
        while (current_byte < bytes_per_block):
            for block in range(len(correction_blocks)):
                result_list.append(
                    correction_blocks[block][current_byte]
                )
            current_byte += 1

        return result_list

    @staticmethod
    def bytes2bits(bytes_list: list[int]) -> str:
        return "".join(f"{byte:08b}" for byte in bytes_list)

    def calculate_module_size(self, qr_code_size=300) -> tuple[int, int]:
        if self.version_number is not None:
            modules_num = 21 + (self.version_number - 1) * 4

            while qr_code_size % modules_num != 0:
                qr_code_size += 1
            pixels_num_per_module = qr_code_size // modules_num

        return qr_code_size, pixels_num_per_module

    @staticmethod
    def module_drawing(
        module_size: int,
        image: Image.Image,
        x: int,
        y: int,
        color: Color
    ) -> None:
        
        if image is not None:
            draw = ImageDraw.Draw(image, "RGBA")

            color_channel = (0, 0, 0, 255) if color is Color.BLACK else (255, 255, 255, 255)

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

    def gen_search_pattern(self, image: Image.Image, module_size: int) -> None:
        modules_number = self.get_modules_number()

        def draw_search_pattern(
                x: int,
                y: int,
                exclude_border: Border
            ) -> None:

            match exclude_border:
                case Border.TOP_LEFT:
                    for i in range(7):
                        for j in range(7):
                            self.module_drawing(module_size, image, x + i, y + j, color=Color.BLACK)
                    for i in range(5):
                        for j in range(5):
                            self.module_drawing(module_size, image, x + i + 1, y + j + 1, Color.WHITE)
                    for i in range(3):
                        for j in range(3):
                            self.module_drawing(module_size, image, x + i + 2, y + j + 2, Color.BLACK)
                    for i in range(7):
                        self.module_drawing(module_size, image, 7, i, Color.WHITE)
                    for i in range(8):
                        self.module_drawing(module_size, image, i, 7, Color.WHITE)
            
                case Border.TOP_RIGHT:
                    for i in range(7):
                        for j in range(7):
                            self.module_drawing(module_size, image, x - i, y + j, Color.BLACK)
                    for i in range(5):
                        for j in range(5):
                            self.module_drawing(module_size, image, x - i - 1, y + j + 1, Color.WHITE)
                    for i in range(3):
                        for j in range(3):
                            self.module_drawing(module_size, image, x - i - 2, y + j + 2, Color.BLACK)
                    for i in range(7):
                        self.module_drawing(module_size, image, x - 7, i, Color.WHITE)
                    for i in range(8):
                        self.module_drawing(module_size, image, x - i, 7, Color.WHITE)
            
                case Border.BOTTOM_LEFT:
                    for i in range(7):
                        for j in range(7):
                            self.module_drawing(module_size, image, x + i, y - j, Color.BLACK)
                    for i in range(5):
                        for j in range(5):
                            self.module_drawing(module_size, image, x + i + 1, y - j - 1, Color.WHITE)
                    for i in range(3):
                        for j in range(3):
                            self.module_drawing(module_size, image, x + i + 2, y - j - 2, Color.BLACK)
                    for i in range(7):
                        self.module_drawing(module_size, image, 7, y - i, Color.WHITE)
                    for i in range(8):
                        self.module_drawing(module_size, image, i, y - 7, Color.WHITE)

        draw_search_pattern(0, 0, exclude_border=Border.TOP_LEFT)
        
        if modules_number >= 7:
            draw_search_pattern(modules_number - 1, 0, exclude_border=Border.TOP_RIGHT)
            draw_search_pattern(0, modules_number - 1, exclude_border=Border.BOTTOM_LEFT)

    def alignment_pattern_drawing(
        self,
        module_size: int,
        image: Image.Image,
        x: int,
        y: int
    ) -> None:
        
        for i in range(5):
            for j in range(5):
                self.module_drawing(
                    module_size, 
                    image, 
                    x + i - 2, 
                    y + j - 2, 
                    color=Color.BLACK
                )

        for i in range(3):
            for j in range(3):
                self.module_drawing(module_size, image, x - 1 + i, y - 1 + j, Color.WHITE)

        self.module_drawing(module_size, image, x, y, Color.BLACK)

    def gen_alignment_pattern(self, image: Image.Image, module_size) -> None:
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
                # MISHKA: Лучше в перспективе это вынести в отдельные методы с говорящими названиями, а не пояснять в комментариях
                # Находится ли точка внутри выравнивающего узора?
                if ax - 2 <= x <= ax + 2 and (ay - 2 <= y <= ay + 2):
                    return True
        return False

    def gen_sync_bands(self, image: Image.Image, module_size) -> None:
        modules_number = self.get_modules_number()
        x = 8
        y = 6
        stripe_color = Color.BLACK

        while x < modules_number - 7:

            if not self.is_in_alignment_pattern(x, y):
                self.module_drawing(module_size, image, x, y, stripe_color)

            stripe_color = ~stripe_color
            x += 1
        
        x = 6
        y = 8
        stripe_color = Color.BLACK

        while y < modules_number - 7:

            if not self.is_in_alignment_pattern(x, y):
                self.module_drawing(module_size, image, x, y, stripe_color)

            stripe_color = ~stripe_color
            y += 1

    def draw_version_code(
        self,
        offset_x: int,
        offset_y: int,
        image: Image.Image,
        module_size
    ) -> None:
        
        version_code = tables.VERSION_CODES[self.version_number]

        for i in range(len(version_code)):
            color = Color.BLACK if version_code[i] == "1" else Color.WHITE

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
    def apply_mask(x: int, y: int, mask_num: int):
        masks = {
            0: (x + y) % 2,
            1: y % 2,
            2: x % 3,
            3: (x + y) % 3,
            4: (x / 3 + y / 2) % 2,
            5: (x * y) % 2 + (x * y) % 3,
            6: ((x * y) % 2 + (x * y) % 3) % 2,
            7: ((x * y) % 3 + (x + y) % 2) % 2,
        }
        return masks[mask_num]

    @staticmethod
    def masking(x: int, y: int, mask_num: int, color: str) -> str:
        if CodeGeneration.apply_mask(x, y, mask_num) == 0:
            color = Color.BLACK
        return color

    def draw_mask_code(self, mask: int, image: Image.Image, module_size) -> None:
        modules_number = self.get_modules_number()
        code = tables.MASK_CODE[mask]
        j = 0

        self.module_drawing(module_size, image, 8, modules_number - 8, Color.BLACK)

        for i in range(7):
            color = Color.WHITE if code[i] == "0" else Color.BLACK
            self.module_drawing(module_size, image, 8, modules_number - 1 - i, color)

            if j == 6:
                j += 1

            self.module_drawing(module_size, image, j, 8, color)
            j += 1

        j = 0

        for i in range(7, len(code)):

            color = Color.WHITE if code[i] == "0" else Color.BLACK
            
            self.module_drawing(
                module_size, image, modules_number - 8 + i - 7, 8, color
            )

            if j == 2:
                j += 1
            
            self.module_drawing(module_size, image, 8, 8 - j, color)
            j += 1

    def is_in_mask_code_or_correction_level(self, x: int, y: int) -> bool:
        modules_number = self.get_modules_number()

        # Вертикальная полоса маски и уровня коррекции (x = 8)
        if x == 8 and (y < 9 or y >= modules_number - 8):
            return True

        # Горизонтальная полоса маски и уровня коррекции (y = 8)
        if y == 8 and (x < 9 or x >= modules_number - 8):
            return True

        # Центральный черный модуль
        if x == 8 and y == 8:
            return True

        return False

    def is_in_finder_pattern(self, x: int, y: int) -> bool:
        # Поисковые узоры находятся в фиксированных позициях (7x7 модулей)
        if (0 <= x <= 6 and 0 <= y <= 6):  # Верхний левый
            return True
        if (0 <= x <= 6 and self.get_modules_number() - 7 <= y <= self.get_modules_number() - 1):  # Нижний левый
            return True
        if (self.get_modules_number() - 7 <= x <= self.get_modules_number() - 1 and 0 <= y <= 6):  # Верхний правый
            return True
    
        return False

    @staticmethod
    def is_empty_module(module_size: int, image: Image.Image, x: int, y: int) -> bool:
        for i in range(x * module_size, (x + 1) * module_size - 1):
            for j in range(y * module_size, (y + 1) * module_size - 1):
                pixel = image.getpixel((i, j))
                
                if isinstance(pixel, tuple) and len(pixel) == 4:
                    if pixel[3] != 0:
                        return False
        return True
    
    def fill_qr_data(self, image: Image.Image, qr_data: str, module_size, mask_num) -> None:
        modules_number = self.get_modules_number()
        data_index = 0

        col = modules_number - 1
        direction = -1

        while col >= 0:
            if col == 6:
                col -= 1
                continue

            start = 0 if direction == 1 else modules_number - 1
            end = modules_number if direction == 1 else -1

            for row in range(start, end, direction):
                for x_offset in range(2):
                    x = col - x_offset
                    y = row

                    if self.is_empty_module(module_size, image, x, y):
                        if data_index < len(qr_data):
                            color = Color.WHITE if qr_data[data_index] == "0" else Color.BLACK
                            color = self.masking(x, modules_number - y - 1, mask_num, color)
                            self.module_drawing(module_size, image, x, y, color)
                            data_index += 1

                        else:
                            color = Color.WHITE
                            color = self.masking(x, modules_number - y - 1, mask_num, color)
                            self.module_drawing(
                                module_size, image, x, y, color
                            )
            direction = -direction
            col -= 2