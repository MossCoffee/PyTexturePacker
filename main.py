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
import argparse

#pass in a "target Directory here - use it to modify image locations, and output"
#right now we're using a shortcut to fill in the file path & we want to pass it in instead
def pack(targetDirectory):
    if targetDirectory == None:
        targetDirectory = ""
    # create a MaxRectsPacker
    packer = Packer.create(max_width=4096, max_height=4096)
    packer.trim_mode = 1
    
    # pack texture images under the directorys "outlines/" and "colors/" and name the output images "test_case".
    # all images will be packed using the uvs of the images from the first directory
    imageLocations = [targetDirectory + "outlines/", targetDirectory + "colors/"]
    packer.packWithMatchingUVs(imageLocations, "test_image%d", targetDirectory + "output/")

def pack_test():
    # create a MaxRectsPacker
    packer = Packer.create(max_width=4096, max_height=4096, bg_color=0xffffff00)
    
    # pack texture images under the directory "test_case/" and name the output images as "test_case".
    # "%d" in output file name "test_case%d" is a placeholder, which is a multipack index, starting with 0.
    packer.pack("outlines/", "test_image%d", "")

def main():
    #this is where we're going to pass it in (probably)
    parser = argparse.ArgumentParser(description='pack two sets of textures in seperate texture sheets where one set maps on to the other [named outlines/ and colors/]')
    parser.add_argument('--path', dest='path', type=str, help="Change target location for outlines/ and colors/ folders")
    args = parser.parse_args()
    pack(args.path)


if __name__ == '__main__':
    main()
