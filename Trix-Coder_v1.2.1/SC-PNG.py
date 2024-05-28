import os
import sys
import lzma
import shutil
import struct
import random
import binascii
import platform

sys.path.append('./System')

from BytesWorker import *
from PIL import Image

folder = "./1сюда-SC/"
folder_export = "./2отсюда-PNG/"
SystemName = platform.system()

def Clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def GameSelect():

    global Game

    print('1 - Бравл Старс')
    print('2 - Клэш Рояль')
    Game = input('выбери игру: ')

    if Game != '1' and Game != '2':

        Clear()
        GameSelect()

Clear()
GameSelect()
Clear()

def _(message):
    print("[INFO] " + message)

def convert_pixel(pixel, type):
    if type == 0:  # RGB8888
        return struct.unpack('4B', pixel)
    elif type == 2:  # RGB4444
        pixel, = struct.unpack('<H', pixel)
        return (((pixel >> 12) & 0xF) << 4, ((pixel >> 8) & 0xF) << 4,
                ((pixel >> 4) & 0xF) << 4, ((pixel >> 0) & 0xF) << 4)
    elif type == 4:  # RGB565
        pixel, = struct.unpack("<H", pixel)
        return (((pixel >> 11) & 0x1F) << 3, ((pixel >> 5) & 0x3F) << 2, (pixel & 0x1F) << 3)
    elif type == 6:  # LA88
        pixel, = struct.unpack("<H", pixel)
        return ((pixel >> 8), (pixel >> 8), (pixel >> 8), (pixel & 0xFF))
    elif type == 10:  # L8
        pixel, = struct.unpack("<B", pixel)
        return (pixel, pixel, pixel)
    else:
        raise Exception("полученя типа пиксиля: " + type)

def decompileSC(fileName):
    baseName = os.path.splitext(os.path.basename(fileName))[0]

    with open(fileName, "rb") as fh:
        data = fh.read()

        if data[0] != 93:
            data = data[26:]

        xbytes = b'\xff' * 8
        ybytes = b'\x00' * 4

        if Game == '1':
            data = data[0:5] + xbytes + data[9:]
        if Game == '2':
            data = data[0:9] + ybytes + data[9:]
        decompressed = lzma.LZMADecompressor().decompress(data)

        i = 0
        picCount = 0

        _("сбор информации...")

        while len(decompressed[i:]) > 5:
            fileType = decompressed[i]
            fileSize, = struct.unpack("<I", decompressed[i + 1:i + 5])
            subType = decompressed[i + 5]
            width, = struct.unpack("<H", decompressed[i + 6:i + 8])
            height, = struct.unpack("<H", decompressed[i + 8:i + 10])

            i += 10

            if subType == 0:
                pixelSize = 4
            elif subType == 2 or subType == 4 or subType == 6:
                pixelSize = 2
            elif subType == 10:
                pixelSize = 1
            else:
                raise Exception("полученя типа пиксиля: " + subType)

            xfilename = fileName[::-1]
            xfilename = xfilename[:xfilename.index('/')]
            xfilename = xfilename[::-1]

            _("название: %s, тип: %s, размер: %s, подтип: %s, ширина: %s, высота: %s" % (xfilename, fileType, fileSize, subType, width, height))
            _("создание картинки...")

            img = Image.new("RGBA", (width, height))

            pixels = []

            for y in range(height):
                for x in range(width):
                    pixels.append(convert_pixel(decompressed[i:i + pixelSize], subType))
                    i += pixelSize

            img.putdata(pixels)

            if fileType == 28 or fileType == 27:
                imgl = img.load()
                iSrcPix = 0
                for l in range(int(height / 32)):
                    for k in range(int(width / 32)):
                        for j in range(32):
                            for h in range(32):
                                imgl[h + (k * 32), j + (l * 32)] = pixels[iSrcPix]
                                iSrcPix += 1
                    for j in range(32):
                        for h in range(width % 32):
                            imgl[h + (width - (width % 32)), j + (l * 32)] = pixels[iSrcPix]
                            iSrcPix += 1

                for k in range(int(width / 32)):
                    for j in range(int(height % 32)):
                        for h in range(32):
                            imgl[h + (k * 32), j + (height - (height % 32))] = pixels[iSrcPix]
                            iSrcPix += 1

                for j in range(height % 32):
                    for h in range(width % 32):
                        imgl[h + (width - (width % 32)), j + (height - (height % 32))] = pixels[iSrcPix]
                        iSrcPix += 1

            fullname = baseName + ('_' * picCount)

            _("Сахранение в пнг...")
            img.save(folder_export + CurrentSubPath + fullname + ".png", "PNG")
            picCount += 1
            _("Сахраниение завершено" + "\n")

files = os.listdir(folder)
for file in files:
	if file.endswith("_tex.sc"):

		global CurrentSubPath

		ScNameList = []
		for i in file:
			ScNameList.append(i)
		DotIndex = ScNameList.index('.')
		CurrentSubPath = ''.join(ScNameList[:DotIndex]) + '/'
		if os.path.isdir(folder_export + CurrentSubPath) == True:
			shutil.rmtree(folder_export + CurrentSubPath)
		os.mkdir(folder_export + CurrentSubPath)
		decompileSC(folder + file)
