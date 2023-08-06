#!/usr/bin/env python3


from argparse import ArgumentParser
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()


def run():

    parser = ArgumentParser(prog="exifstrip")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("images", nargs="*")

    namespace = parser.parse_args()
    print(namespace)


if __name__ == "__main__":
    run()









# image = Image.open("image-2.heic")

# # next 3 lines strip exif
# data = list(image.getdata())
# image_without_exif = Image.new(image.mode, image.size)
# # image_without_exif.putdata(data)

# # image_without_exif.save('image_file_without_exif.jpeg')

# def dump(img):
#     exif = img.getexif()
#     for tag_id in exif:
#         tag = TAGS.get(tag_id, tag_id)
#         data = exif.get(tag_id)
#         # decode bytes 
#         if isinstance(data, bytes):
#             data = data.decode()
#         print(f"{tag:25}: {data}")

# print("***")

# dump(image)
# print("***")
# dump(image_without_exif)

# print("***")
