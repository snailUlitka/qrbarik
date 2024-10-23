import tables
import qr_code_generation

from qr_code_generation import CodeGeneration
from PIL import Image
from PIL import Image, ImageOps


input = "Kapibara"
bin_unicode_input = "".join(format(ord(ch), "08b") for ch in input)
bin_unicode_length = len(bin_unicode_input)
unicode_len_without_prefix = (str(bin(bin_unicode_length)[2:]))
data_lengthBin = bin_unicode_length / 8
res = "0" + "1" + "0" + "0" + unicode_len_without_prefix[0] + bin_unicode_input

print(f"Рез-т после указания типа кодирования и длины входной строки: {res}")
print("строка в двоичном коде:")
print(bin_unicode_input)
print("Длина строки")
print(bin_unicode_length)
print("длина строки в двоичном коде:")
print(unicode_len_without_prefix)

qr_code = qr_code_generation.CodeGeneration()


version_number = qr_code_generation.versionNumber(bin_unicode_length)
qr_code.set_version_number(version_number)
print(f"Версия: {qr_code.get_version_number}")
print(f"Длина поля: {qr_code_generation.fieldLength(version_number)}")
polynomial = tables.generating_polynomials[str(tables.correction_bytes_per_block[str(version_number)])]
modules_number = 21 + (version_number - 1) * 4   # Количество модулей по горизонтали и вертикали
qr_code.set_modules_number(modules_number)
positions = tables.alignment_pattern[version_number]
qr_code.set_positions(positions)
version_code = tables.version_codes[version_number]
blocks_num = tables.blocks_number[str(version_number)]
qr_code.set_blocks_num(blocks_num)
print(f"Кол-во блоков: {qr_code.get_blocks_num}")
res = qr_code_generation.filling(res)
remainder = (len(res) / 8) % blocks_num
qr_code.set_remainder(remainder)
print(f"Остаток: {qr_code.get_remainder}")
print(f"Рез-т после заполнения: {res}")
print(f"Длина после заполнения: {len(res)}")
block_data_amount = (len(res) / 8) // blocks_num
qr_code.set_block_data_amount(block_data_amount)
print(f"Кол-во данных в блоке: {qr_code.get_block_data_amount}")


def blocksPrinting(qr_code: CodeGeneration, blocks):
    data_amount = qr_code.get_block_data_amount()
    remain = qr_code.get_remainder()
    q = 0
    j = qr_code.get_block_data_amount() * 8

    for i in range(0, int(qr_code.get_blocks_num() - remain)):   # TODO: i
        blocks.append(res[int(q) : int(j)])
        q = data_amount * 8
        j = j + data_amount * 8

    if remain != 0:
        q = data_amount * 8 + 8

        for i in range(0, int(remain)):
            blocks.append(res[int(j) : int(q)])
            j = data_amount * 8 + 8
            q = q + data_amount * 8 + 8
            
    for i in range(len(blocks)):
        print(blocks[i])

blocks = []
blocksPrinting(qr_code, blocks)
print(res)
print(f"Длина первого блока: {len(blocks[0])}")
print("Полином")
print(polynomial)
print(polynomial[0])

blocks = CodeGeneration.blocksBin2DecTranslation(blocks)

print("Блоки в 10-тичной сс")
for i in range(len(blocks)):
    print(blocks[i])

print("Длина первого блока:" + str(len(blocks[0])))
print("Длина второго блока:" + str(len(blocks[1])))
print(blocks[0][1])
print("Байты коррекции")
print(qr_code.binCorrectionCreating(blocks))
print("Объедененные блоки")
# print(combining_blocks(blocks,binCorrectionCreating(blocks)))

DATA_QR = qr_code.combiningBlocks(blocks, qr_code.binCorrectionCreating(blocks))
qr_code.set_DATA_QR(DATA_QR)
print(qr_code.get_DATA_QR)
print(CodeGeneration.bytesToBits(qr_code.get_DATA_QR))

# Рассчитываем размер стороны модуля в пикселях
image_module_size = int(qr_code.imageModuleSizeCalculating()[0] / (21 + (version_number - 1) * 4))

# Пример вызова функции
qr_code.searchPatternGenerating()
qr_code.alignmentPatternGenerating()
qr_code.syncBandsGenerating()

if (qr_code.get_version_number() >= 7):
    CodeGeneration.codeVersionDrawing(version_code, modules_number - 11, 0)

qr_code.maskCodeAndCorrectionLevel()
qr_code.QRDataFilling()
calculation = qr_code.moduleSizeCalculation()
image = Image.new(
            "RGBA",
            (calculation[0], calculation[0]),
            (256, 256, 256, 0),
            )
image = ImageOps.expand(image, border=image_module_size, fill="white")
image.save("finder_pattern.png")
image.show()
