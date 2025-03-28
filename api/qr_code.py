from qr_code_generation import CodeGeneration
from PIL import Image, ImageOps


# TODO: объединить определение целого числа байт и остатка в каждом блоке
# NOTE: utf-8 is recommended for encoding
# TODO: add H-level for adding an image on QR-code 

input_info = "!Kapibara !!! 0_0 Kapibara !!! 0_0 Kapibara !!! 0_0"
version_number, res = CodeGeneration.service_fields(input_info)
qr_code = CodeGeneration(version_number)
binary_blocks, remain, data_per_block = qr_code.bin_blocks_filling(res)
decimal_blocks = CodeGeneration.blocks_bin2dec_translation(binary_blocks)
qr_data = CodeGeneration.bytes2bits(qr_code.blocks_combination(decimal_blocks, qr_code.bin_correction_creating(decimal_blocks), remain, data_per_block))
qr_code_size, pixels_num_per_module = qr_code.module_size_calculation()   # NOTE: у Вики доп. деление

num_modules = 21 + (qr_code.version_number - 1) * 4
module_size = int(qr_code_size / num_modules)

image = Image.new(
    "RGBA",
    (qr_code_size, qr_code_size),
    (256, 256, 256, 0),
)

qr_code.search_pattern_generation(image, module_size)

if qr_code.version_number > 1:
    qr_code.alignment_pattern_generation(image, module_size)

qr_code.sync_bands_generation(image, module_size)

if qr_code.version_number >= 7:
    qr_code.code_version_drawing(qr_code.get_modules_number() - 11, 0, image, module_size)

qr_code.mask_code_and_correction_level(image, module_size)
qr_code.qr_data_filling(image, qr_data, module_size)

image = ImageOps.expand(image, border=4 * module_size, fill="white")
image.save("./api/qr_code.png")
image.show()