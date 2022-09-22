from PIL import Image
import glob

Image.MAX_IMAGE_PIXELS = None


def main(filename):
    original = Image.open(filename)
    image_for_pixel = Image.open(filename)

    original_width, original_height = original.size
    pixel_image_width, pixel_image_height = image_for_pixel.size

    image_for_pixel = crop_center(image_for_pixel, min(pixel_image_width, pixel_image_height),
                                  min(pixel_image_width, pixel_image_height))
    pixel_image_width, pixel_image_height = image_for_pixel.size

    original = original.convert("RGBA")
    data = original.getdata()
    newData = []
    for item in data:
        newData.append(item[:-1] + (int(256 * 0.7),))
    original.putdata(newData)

    original = original.resize((original_width * pixel_image_width, original_height * pixel_image_height))
    image_for_pixel = image_for_pixel.convert("RGBA")
    data = image_for_pixel.getdata()
    newData = []
    for item in data:
        newData.append(item[:-1] + (int(256 * 0.3),))
    image_for_pixel.putdata(newData)

    for x in range(original_width):
        for y in range(original_height):
            original.paste(image_for_pixel, (pixel_image_width * x, pixel_image_height * y), mask=image_for_pixel)
    original = original.convert('RGB')
    original.save(filename)


def crop_center(pil_img: Image, crop_width: int, crop_height: int) -> Image:
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


if __name__ == '__main__':
    for name in glob.glob("D:/videoInVideo/rickroll/**.jpg"):
        main(name)
        print(name + " - finished")
