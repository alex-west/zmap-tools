###################
## Saves textures from Zero Tolerance to a file
##
## requires PyQt

import sys, os

rom = './zerotole.bin'
##romout = './modified.bin'

## Bin functions

def read_bin(f):
    #print("Read: " + f)
    #f = os.path.join(indir, f)
    return open(f,"rb").read()
	
def dump_bin(f,data):
    #print("Dump: " + f)
    #f = os.path.join(outdir, f)
    open(f,"wb").write(data)

## Drawing functions

from PyQt5.QtCore import Qt, QRect

from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QIcon

from PyQt5.QtWidgets import (QMainWindow, qApp, QAction, QFileDialog,
                             QApplication, QVBoxLayout, QLabel)

## Notes on texture format:
##  Textures are 32-by-32 pixel uncompressed 4-bit-per-pixel bitmaps
##
##  Each byte stores the information for two pixels. The upper 4 bits store 
##  the information for the left pixel, and the 4 lower bits store the right
##  pixel.
##
##  Textures are stored in columns with each column being 2 pixels (1 byte) wide
##
##  Given how the Genesis' hardware works, all textures onscreen must use the
##  same 16 color palette.
##
##  Color 0 is transparent, which exposes the "skybox" layer (note: not a box)

def drawPixelPair(bin, offset, palette, x, y, qp):
	pixel = (bin[offset] & 0xF0) >> 4
	qp.setPen(palette[pixel])
	qp.drawPoint(x, y)
	
	pixel = bin[offset] & 0x0F
	qp.setPen(palette[pixel])
	qp.drawPoint(x+1, y)
	
def drawColumn(bin, offset, palette, x, y, qp):
	for row in range(0,32):
		drawPixelPair(bin, offset+row, palette, x, y+row, qp)
	
def drawTexture(bin, offset, palette, x, y, qp):
	for col in range(0,16):
		drawColumn(bin, offset+col*32, palette, x+col*2, y, qp)

## The above three functions inlined together
## It doesn't help performance as much as I hoped
def drawTextureInlined(bin, offset, palette, x, y, qp):
	for col in range(0,16):
		temp_x = x + col*2
		temp_offset = offset + col*32
		
		for row in range(0,32):
			temp_y = y + row
			temp_offset2 = temp_offset + row
			
			pixel = (bin[temp_offset2] & 0xF0) >> 4
			qp.setPen(palette[pixel])
			qp.drawPoint(temp_x, temp_y)
	
			pixel = bin[temp_offset2] & 0x0F
			qp.setPen(palette[pixel])
			qp.drawPoint(temp_x+1, temp_y)
		
def saveOneTexture(bin, offset, palette):
	picture = QPixmap(32, 32)
	qp = QPainter()
	qp.begin(picture)

	drawTexture(data, offset, palette, 0, 0, qp)

	qp.end()
	picture.save('./textures/texture_{0:08X}.png'.format(offset))

def saveManyTextures(bin, offset, count, palette):
	width = 16
	h_size = 32*width
	if (count < width):
		h_size = 32*count
		width = count

	v_size = 32 * ((count + (width-1))//width) ## Ceiling division

	picture = QPixmap(h_size, v_size)
	qp = QPainter()
	qp.begin(picture)
	## TODO: Clear the canvas
	
	for texture in range(count):
		temp_offset = offset + texture*512
		temp_x = (texture%width)*32
		temp_y = (texture//width)*32
	
		drawTexture(data, temp_offset, defaultPalette, temp_x, temp_y, qp)
		
	qp.end()
	picture.save('./textures/textures_0x{0:08X}.png'.format(offset))

## Notes on the metatexture format:
##  In game, every wall takes its textures from the same pool of 255 32x32 wall
##  textures. Each world in the game has a set of definitions that combines
##  these smaller textures into larger (4x2 textures, or 128x64 pixels) textures
##  that I call "metatextures".
##
##  Each metatexture definition is 16 bytes long, and consists of 8 2-byte big
##  endian values. The way these values are ordered is as follows:
##
##     |   |   |   
##   0 | 2 | 4 | 6
##     |   |   |   
##  ---+---+---+---
##     |   |   |   
##   1 | 3 | 5 | 7
##     |   |   |   
##
##  Also, no, I have not been able to find where the SEGA logo's metatexture is
##  defined.
##
##  Also, the billboarded sprites in the game almost certainly have a different
##  format than this one.

def drawMetatexture(bin, offset, palette, x, y, qp):
	walltex_offset = 0x12EF26
	
	for count in range(0,8):
		temp_x = (count//2)*32
		temp_y = (count%2)*32
		
		## Lazily reading the less significant byte of a big endian 2 byte number
		index = bin[offset + count*2 + 1]
		temp_offset = walltex_offset + (index*512)
		
		drawTextureInlined(bin, temp_offset, palette, x+temp_x, y+temp_y, qp)	

def saveOneMetatexture(bin, offset, palette):
	picture = QPixmap(32*4, 32*2)
	qp = QPainter()
	qp.begin(picture)
	
	drawMetatexture(data, offset, palette, 0, 0, qp)
	
	qp.end()
	picture.save('./textures/metatexture_0x{0:08X}.png'.format(offset))

def saveManyMetatextures(bin, offset, count, palette):
	width = 16
	h_size = 128*width
	if (count < width):
		h_size = 32*count
		width = count

	v_size = 64 * ((count + (width-1))//width) ## Ceiling division
	
	picture = QPixmap(h_size, v_size)
	qp = QPainter()
	qp.begin(picture)
	
	for metaTexture in range(count):
		##print(metaTexture)  ##debug count
		temp_x = (metaTexture%width)*128
		temp_y = (metaTexture//width)*64
		temp_offset = offset + metaTexture*16
		
		drawMetatexture(bin, temp_offset, palette, temp_x, temp_y, qp)
		
	qp.end()
	picture.save('./textures/metatextures_0x{0:08X}.png'.format(offset))
	
## Palette data

## TODO: Locate palette data in ROM and convert it automagically
defaultPalette = [ QColor(255,0,255), ## Transparent (is actually (0,0,0))
                   QColor(0,36,72),
                   QColor(72,108,144),
				   QColor(144,180,216),
				   
				   QColor(216,216,252),
				   QColor(36,36,0),
				   QColor(72,72,0),
				   QColor(36,108,252),
				   
				   QColor(72,0,0),
				   QColor(108,36,0),
				   QColor(252,144,72),
				   QColor(144,72,36),
				   
				   QColor(252,252,180),
				   QColor(216,36,0),
				   QColor(72,144,36),
				   QColor(0,0,0)
                   ]
				   
## Main procedure
## Uncomment the line you want done

data = read_bin(rom)
app = QApplication(sys.argv)

## Save one texture
textureTest_offset = 0x10E9BE
##saveOneTexture(data, textureTest_offset, defaultPalette)

## Save all of the wall textures
walltex_offset = 0x12EF26
walltex_count = 255
##saveManyTextures(data, walltex_offset, walltex_count, defaultPalette)

## Save every set of textures
## Not a very pythonic way of doing this
textureOffsets = [0x10E9BE, 0x12EF26, 0x1726F2, 0x178C80, 0x17EB94, 0x184478, 0x18EB00, 0x19450C, 0x19DC28, 0x1A8872, 0x1AD938, 0x1BAF8A, 0x1C656A, 0x1CBA34, 0x1CC338]
textureCounts = [66, 255, 47, 23, 40, 70, 42, 72, 78, 34, 81, 59, 42, 3, 24]
for x in range(15):
	##saveManyTextures(data, textureOffsets[x], textureCounts[x], defaultPalette)

## Save one metatexture	
metatextureTest_offset = 0x15A52A
##saveOneMetatexture(data, metatextureTest_offset, defaultPalette)

## Save every set of metatextures
metatextureOffsets = [0x15a10a, 0x160424, 0x16602C]
metatextureCount = 256
for x in range(3):
	saveManyMetatextures(data, metatextureOffsets[x], metatextureCount, defaultPalette)

##
## Coda: Notes on the ZMAP format
## 
## Zero Tolerance stores its worlds in a format called "ZMAP"
##
## The format, as far as i've bothered deciphering it, goes something like this:
##  4 bytes - ASCII header saying "ZMAP"
##  4096 bytes - 256 metatexture definitions (16 bytes each)
##  2048 bytes - 256 map block metatexture assignments (8 bytes each) (todo: verify)
##   - looks like 4 2-byte big endian values each (corresponding to compass directions?)
##  256 bytes - map block properties (todo: verify, decipher)
##  1024 bytes - one 32x32 level (each map block is one byte)
##   - repeat for 16 levels (not all are used)
##  ~3000 bytes - some other kind of data (seems variable length)
## 
## There are three ZMAP files in the game, located right next to each other, 
## each corresponding to one of the game's worlds:
##  0x15A106 -- Spaceship
##   - 0x15A10A -- Metatexture definitions
##   - 0x15B10A -- Map block metatexture assignments (todo: verify)
##   - 0x15B90A -- Map block properties (todo: verify)
##   - 0x15BA0A -- Level data
##   - 0x15FA0A -- Unknown
##  0x160420 -- Highrise apartment
##   - etc.
##  0x166028 -- Basement
##   - etc.
##
## Beyond Zero Tolerance also has sections of ROM labeled "ZMAP". It has five:
##  0x0AAE2C, 0x0AF4F2, 0x0B44BA, 0x148582, 0x14E18A
##
## (Cursory examination suggests the last two ZMAPs are leftovers from the last 
## two worlds from ZT.)
##
## BZT's ZMAP format is slightly different, in that it appears to support a 
## variable amount of levels per world, and the size of the levels is also 
## variable. However, the basic structure appears to be similar at first glance.
##
## romhacking.net has a level editor for ZT and BZT that was helpful for
## figuring some of this out. However, it is not capable of viewing wall
## textures and such while editing, and it does not support editing any data
## in the ZMAPs besides the level data, so it is a bit impractical to use.
##
## You can find it here: https://www.romhacking.net/utilities/621/
##

# EoF