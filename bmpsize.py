import base64, struct
with open('d:\\test\\bmp\\QQsnip.bmp', 'rb') as f:
    s = f.read(30)
print(s)
def bmp_info():
    unpackbuf = struct.unpack('<ccIIIIIIHH', s)
    if (unpackbuf[0] != b'B' or unpackbuf[1] != b'M'):
        return None
    else:
        return { 'width' : unpackbuf[6], 'height': unpackbuf[7]   }
bi = bmp_info()
print( bi['height'], bi['width'])
