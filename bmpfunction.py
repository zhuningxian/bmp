from PIL import Image
file_path = 'd:\\test\\bmp\\QQsnip.bmp'
img = Image.open(file_path)
imgSize = img.size#大小/尺寸
w = img.width#图片的宽
h = img.height#图片的高
f = img.format#图像格式
print(imgSize)
print(w,h,f)
