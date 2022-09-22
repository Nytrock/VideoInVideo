from PIL import Image
import glob

num = 0
for name in glob.glob("MainVideo/**.jpg"):
    image = Image.open(name)
    image = image.resize((8192, 6144))
    image.save(name)
    num += 1
    print(name, "- finished")
