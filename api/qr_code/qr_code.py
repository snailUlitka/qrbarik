from qr_code_generation import CodeGeneration
from PIL import Image, ImageOps


# TODO: объединить определение целого числа байт и остатка в каждом блоке
# NOTE: utf-8 is recommended for encoding
# TODO: add H-level for adding an image on QR-code 

input_info = "Kapibara" * 100
version_number, res = CodeGeneration.service_fields(input_info)
qr_code = CodeGeneration(version_number)
binary_blocks, remain, bytes_per_block = qr_code.fill_blocks(res)
decimal_blocks = CodeGeneration.translate_blocks_to_dec(binary_blocks)

bin_correction = qr_code.create_error_correction(decimal_blocks)

combined_blocks = qr_code.combinate_blocks(
    decimal_blocks,
    bin_correction,
    remain,
    bytes_per_block
)

qr_data = CodeGeneration.bytes2bits(combined_blocks)

qr_code_size, module_size = qr_code.calculate_module_size()

image = Image.new(
    "RGBA",
    (qr_code_size, qr_code_size),
    (256, 256, 256, 0),
)

qr_code.gen_search_pattern(image, module_size)

if qr_code.version_number > 1:
    qr_code.gen_alignment_pattern(image, module_size)

qr_code.gen_sync_bands(image, module_size)

if qr_code.version_number > 6:
    qr_code.draw_code_version(qr_code.get_modules_number() - 11, 0, image, module_size)

mask = 3

qr_code.draw_mask_code(mask, image, module_size)
qr_code.fill_qr_data(image, qr_data, module_size, mask)

image = ImageOps.expand(image, border=4 * module_size, fill="white")
image.save("../Sources/qr_code.png")
image.show()