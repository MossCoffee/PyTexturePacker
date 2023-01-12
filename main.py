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
import NormalMapGen
import argparse


def pack(targetDirectory):
    if targetDirectory == None:
        targetDirectory = "" #local directory
    
    packer = Packer.create(max_width=4096, max_height=4096,trim_mode=1,bg_color=(255,255,255,255),border_padding=5,reduce_border_artifacts=False,enable_rotated=False)
    
    inputFolderNames = ["outlines", "colors", "masks"]
    return packer.packWithMatchingUVs(inputFolderNames, "output" , targetDirectory)

def main():
    parser = argparse.ArgumentParser(description='pack two sets of textures in seperate texture sheets where one set maps on to the other [named outlines/ and colors/]')
    parser.add_argument('-p', '--path', default="", dest='path', type=str, help="Change target location for outlines/ and colors/ folders")
    parser.add_argument('-n', '--normals', default=False, dest='normalsEnabled', type=bool, help="Enable the generation of normal map using the colors generated from output")
    parser.add_argument('-s', '--smooth', default=0., type=float, help='requires --normals smooth gaussian blur applied on the image')
    parser.add_argument('-it', '--intensity', default=1., type=float, help='requires --normals intensity of the normal map')

    args = parser.parse_args()
    filePathList = pack(args.path) #this should create a temp folder
    #invert outlines & put it on a black background
    #greyscale the colors & put it on a black background
    #make temp variant of the colors where all transparent pixels are black & all opaque pixels are white
    #generate normals using the temp variant
    NormalMapGen.generateNormals("colors", args.path, args.smooth, args.intensity)
    #put masks on a black background

if __name__ == '__main__':
    main()
