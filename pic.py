from PIL import Image
import hashlib

md5hash = hashlib.md5(Image.open('goblyns-01.png').tobytes())
print(md5hash.hexdigest())
