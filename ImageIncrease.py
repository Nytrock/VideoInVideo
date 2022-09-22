from PIL import Image
import glob

num = 0


def crop_center(pil_img: Image, crop_width: int, crop_height: int) -> Image:
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


for name in glob.glob("SizingVideo/**.jpg"):
    image = Image.open(name)
    image = crop_center(image, 27648 // 8, 20736 // 8)
    image.save(name)
    num += 1
    print(name, "- finished")
