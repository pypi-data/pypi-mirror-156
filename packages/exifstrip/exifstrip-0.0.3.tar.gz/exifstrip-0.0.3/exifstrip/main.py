#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()


def run():

    parser = ArgumentParser(prog="exifstrip")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("images", nargs="*")

    namespace = parser.parse_args()
    
    for path_string in namespace.images:

        image_path = Path(path_string)
        absolute = str(image_path.absolute())

        if not (image_path.exists() and image_path.is_file()):
            print(f"Error: {image_path} does not exist or is not a file")
            continue

        image = Image.open(absolute)

        data = list(image.getdata())
        image_no_exif = Image.new(image.mode, image.size)
        image_no_exif.putdata(data)

        if namespace.overwrite:
            destination = absolute
        
        else:
            suffixes = "".join(image_path.suffixes)
            destination = absolute.rstrip(suffixes) + ".stripped" + suffixes

        image_no_exif.save(destination)

        # verify stripped
        image = Image.open(Path(destination))
        exif = image.getexif()
        if len(exif) != 0:
            print(f"Error: EXIF data from resulting image is not empty, has {len(exif)} entries.")

if __name__ == "__main__":
    run()
