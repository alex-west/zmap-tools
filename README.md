# zmap-tools

Tools for the Genesis FPS "Zero Tolerance"

Currently saves textures from Zero Tolerance to a file.

dependencies: PyQt

# Notes on texture format

Textures are 32-by-32 pixel uncompressed 4-bit-per-pixel bitmaps. Each byte stores the information for two pixels. The upper 4 bits store the information for the left pixel, and the 4 lower bits store the right pixel. Textures are stored in columns with each column being 2 pixels (1 byte) wide.

Given how the Genesis' hardware works, all textures onscreen must use the same 16 color palette. Color 0 is transparent, which exposes the "skybox" layer (note: not a box) to the player.

# Notes on the metatexture format:

In game, every wall takes its textures from the same pool of 255 32x32 wall textures. Each world in the game has a set of definitions that combines these smaller textures into larger (4x2 textures, or 128x64 pixels) textures that I call "metatextures".

Each metatexture definition is 16 bytes long, and consists of 8 2-byte big endian values. The way these values are ordered is as follows:
 
 0 | 2 | 4 | 6
---|---|---|---
 1 | 3 | 5 | 7

(The game's billboarded sprites appear to use a different format.)

# Notes on the ZMAP format

Zero Tolerance stores its worlds in a format called "ZMAP".

The format, as far as i've bothered deciphering it, goes something like this:
  * 4 bytes - ASCII header saying "ZMAP"
  * 4096 bytes - 256 metatexture definitions (16 bytes each)
  * 2048 bytes - 256 map block metatexture assignments (8 bytes each) (todo: verify)
    * looks like 4 2-byte big endian values each (corresponding to compass directions?)
  * 256 bytes - map block properties (todo: verify, decipher)
  * 1024 bytes - one 32x32 level (each map block is one byte)
    * repeat for 16 levels (not all are used)
  * ~3000 bytes - unknown data (length varies)

There are three ZMAP files in the game, located right next to each other, each corresponding to one of the game's worlds:
  * 0x15A106 -- Spaceship
    * 0x15A10A -- Metatexture definitions
    * 0x15B10A -- Map block metatexture assignments (todo: verify)
    * 0x15B90A -- Map block properties (todo: verify)
    * 0x15BA0A -- Level data
    * 0x15FA0A -- Unknown
  * 0x160420 -- Highrise apartment
  * 0x166028 -- Basement

Beyond Zero Tolerance also has sections of ROM labeled "ZMAP". It has five:
  * 0x0AAE2C
  * 0x0AF4F2
  * 0x0B44BA
  * 0x148582
  * 0x14E18A

(Cursory examination suggests the last two ZMAPs are leftovers from the last two worlds from Zero Tolerance.)

BZT's ZMAP format is slightly different, in that it appears to support a variable amount of levels per world, and variable level sizes. However, the basic structure appears to be similar, at least at first glance.

romhacking.net has a level editor for ZT and BZT that was helpful for figuring some of this out. However, it is not capable of viewing wall textures and such while editing, and it does not support editing any data in the ZMAPs besides the level data, so it is a bit impractical to use.

You can find it here: https://www.romhacking.net/utilities/621/
