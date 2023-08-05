#!/usr/bin/env python3

import click
from PIL import Image
from PIL import ImageOps


def square(image):
    w, h = image.size
    if w == h: return image
    short_edge = min(w, h)
    if short_edge == w:
        offset = round((h - w) / 2)
        crop_box = (0, offset, short_edge, offset+short_edge)
    else:
        offset = round((w - h) / 2)
        crop_box = (offset, 0, offset+short_edge, short_edge)
    return image.crop(crop_box)


@click.command()
@click.option('--gray', '-g', help="Generate gray image.",
              is_flag=True)
@click.argument("FILENAME")
@click.argument("SIZE", nargs=-1)
def cli(filename, size, gray):
    if not size:
        size = (16, 32, 48, 128)
    else:
        size = [int(x) for x in size]

    src_image = Image.open(filename, "r")
    src_image = square(src_image)

    for size in size:
        icon = src_image.resize((size, size), Image.LANCZOS)
        icon.save("icon{size}.png".format(size=size))
        if gray:
            grayscale_icon = ImageOps.grayscale(icon)
            grayscale_icon.save("icon{size}-disable.png".format(size=size))


if __name__ == "__main__":
    cli()
