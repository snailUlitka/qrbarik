import tables

from qr_code_generation import CodeGeneration
from PIL import Image
from PIL import Image, ImageOps


def bin_blocks_filling(res: str, qr_code: CodeGeneration, remain: float) -> list[str]:
    data_amount = qr_code.block_data_amount
    binary_blocks: list[str] = []
    q = 0
    j = qr_code.block_data_amount * 8

    for i in range(
        int(qr_code.blocks_num - remain)
    ):   
        
        binary_blocks.append(res[int(q):int(j)])
        q = data_amount * 8
        j = j + data_amount * 8

    if remain != 0:
        q = data_amount * 8 + 8

        for i in range(int(remain)):
            binary_blocks.append(res[int(j):int(q)])
            j = data_amount * 8 + 8
            q = q + data_amount * 8 + 8

    return binary_blocks

res = ""

def qr_code_init(input: str) -> CodeGeneration:
    bin_unicode_input = "".join(format(ord(ch), "08b") for ch in input)
    bin_unicode_length = len(bin_unicode_input)
    version_number = CodeGeneration.define_version(bin_unicode_length)
    modules_number = 21 + (version_number - 1) * 4   # Количество модулей по горизонтали и вертикали
    positions = tables.ALIGNMENT_PATTERN.get(version_number)
    version_code = tables.VERSION_CODES.get(version_number)
    blocks_num = tables.BLOCKS_NUMBER[version_number]    
    unicode_len_without_prefix = str(bin(bin_unicode_length))[2:]
    res = f"0100{unicode_len_without_prefix[0]}{bin_unicode_input}"
    res = CodeGeneration.filling(version_number, res)
    remainder = len(res) / 8 % blocks_num
    block_data_amount = len(res) / 8 // blocks_num

    qr_code = CodeGeneration(version_number, modules_number, positions, 
                             version_code, blocks_num, remainder, block_data_amount)
    
    return qr_code


def qr_code_gen(qr_code: CodeGeneration, res: str):
    polynomial = tables.GENERATING_POLYNOMIALS[
        tables.CORRECTION_BYTES_PER_BLOCK[qr_code.version]
    ]  
    data_amount = qr_code.block_data_amount
    remain = qr_code.remainder
    binary_blocks = bin_blocks_filling(res, qr_code, remain)
    decimal_blocks = CodeGeneration.blocks_bin2dec_translation(binary_blocks)
    DATA_QR = qr_code.blocks_combination(decimal_blocks, qr_code.bin_correction_creating(decimal_blocks))
    qr_code.set_DATA_QR(DATA_QR)
    image_module_size = (
        int(qr_code.module_size_calculation()[0] 
        / (21 + (qr_code.version - 1) * 4))
    )
    qr_code.search_pattern_generating()
    qr_code.alignment_pattern_generation()
    qr_code.sync_bands_generation()

    if qr_code.version >= 7:
        qr_code.code_version_drawing(qr_code.version_code, qr_code.modules_number - 11, 0)

    qr_code.mask_code_and_correction_level()
    qr_code.qr_data_filling()
    calculation = qr_code.module_size_calculation()
    image = Image.new(
        "RGBA",
        (calculation[0], calculation[0]),
        (256, 256, 256, 0),
    )
    image = ImageOps.expand(image, border=image_module_size, fill="white")
    image.save("./api/qr_code.png")
    image.show()

qr_code = qr_code_init('Kapibara')
qr_code_gen(qr_code, res)

#print(f'ASCII-коды входной строки в бинарном формате: {bin_unicode_input}\n\n \
#Длина строки в бинарном формате без префикса: {unicode_len_without_prefix}\n\n \
#Рез-т после указания типа кодирования и длины входной строки:\n {res}\n\n \
#Номер версии: {qr_code.get_version_number()}\n\n \
#Длина поля: {CodeGeneration.field_length(qr_code.get_version_number())}\n\n \
#Кол-во блоков: {qr_code.get_blocks_num()}\n\n \
#Остаток: {qr_code.get_remainder()}\n\n \
#Рез-т после заполнения: \n{res}\n\n\
#Длина после заполнения: {len(res)}\n\n \
#Кол-во данных в блоке: {qr_code.get_block_data_amount()}\n\n \
#Длина первого блока: {len(binary_blocks[0])}\n\n \
#Полином: {polynomial}\n\n \
#Первый элемент многочлена: {polynomial[0]}\n\n \
#Блоки в 10-тичной сс:\n'
#)
#
#for i in range(len(binary_blocks)):
#    print(f'{i + 1} блок:\n {binary_blocks[i]}\n')
#
#for i in range(len(decimal_blocks)):
#    print(decimal_blocks[i], '\n')
#
#for i in range(len(decimal_blocks)):
#    print(f'Длина {i + 1}-го блока: {len(decimal_blocks[i])}')
#
#print(f'\nПервый элемент первого блока: {decimal_blocks[0][0]}\n\n \
#Байты коррекции:\n \
#{qr_code.bin_correction_creating(decimal_blocks)}\n\n \
#Объединенные блоки:\n \
#{qr_code.get_DATA_QR()}\n \
#{CodeGeneration.bytes2bits(qr_code.get_DATA_QR())}'
#)