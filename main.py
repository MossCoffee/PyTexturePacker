# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Authors:
    Huang Quanyong (wo1fSea) quanyongh@foxmail.com
    Taylor Riviera
Date:
    2020/06/26
Description:
    main.py
----------------------------------------------------------------------------"""

from PyTexturePacker import Packer


def pack():
    # create a MaxRectsPacker
    packer = Packer.create(max_width=2048, max_height=2048, bg_color=0xffffff00)
    # pack texture images under the directorys "outlines/" and "colors/" and name the output images "test_case".
    # all images will be packed using the uvs of the images from the first directory
    imageLocations = ["outlines/", "colors/"]
    packer.packWithMatchingUVs(imageLocations, "test_image%d", "")


def main():
    pack()


if __name__ == '__main__':
    main()
