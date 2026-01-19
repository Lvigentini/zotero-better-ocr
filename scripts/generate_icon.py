import os
import zlib
import struct

def make_png(width, height, red, green, blue):
    # Very basic raw PNG generator
    def I1(value):
        return struct.pack("!B", value & (2**8-1))
    def I4(value):
        return struct.pack("!I", value & (2**32-1))
    
    # Header
    png = b"\x89PNG\r\n\x1a\n"
    
    # IHDR: width, height, bit_depth, color_type, compression, filter, interlace
    ihdr = I4(width) + I4(height) + I1(8) + I1(2) + I1(0) + I1(0) + I1(0)
    png += I4(len(ihdr)) + b"IHDR" + ihdr + I4(zlib.crc32(b"IHDR" + ihdr))
    
    # IDAT: Data
    # 3 bytes per pixel (RGB)
    raw_data = b""
    for y in range(height):
        raw_data += b"\x00" # filter type 0 (None)
        for x in range(width):
            raw_data += I1(red) + I1(green) + I1(blue)
            
    compressed = zlib.compress(raw_data)
    png += I4(len(compressed)) + b"IDAT" + compressed + I4(zlib.crc32(b"IDAT" + compressed))
    
    # IEND
    png += I4(0) + b"IEND" + I4(zlib.crc32(b"IEND"))
    
    return png

def create_icon():
    # 48x48 Teal Icon
    data = make_png(48, 48, 0, 128, 128)
    
    addon_dir = os.path.join(os.path.dirname(__file__), '..', 'addon')
    icon_path = os.path.join(addon_dir, 'icon.png')
    
    with open(icon_path, 'wb') as f:
        f.write(data)
    print("Created 48x48 icon.png")

if __name__ == "__main__":
    create_icon()
