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
import os
import PIL as Image



def pack(targetDirectory, inputFolderNames):
    packer = Packer.create(max_width=4096, max_height=4096,trim_mode=1,border_padding=5,reduce_border_artifacts=False,enable_rotated=False)
    return packer.packWithMatchingUVs(inputFolderNames, "intermediate", "output", targetDirectory)

def verifyFolderStructure(inPath, inputFolderNames):
    output = True
    outputFolderNames = ["output","intermediate"]
    neededFiles = inputFolderNames + outputFolderNames


    scanPath = os.scandir(path=inPath)
    for file in scanPath:
        if file.is_dir():
            for name in neededFiles:
                if file.name == name:
                    neededFiles.remove(name)
                    break
    
    if len(neededFiles) > 0:
        for name in neededFiles:
            if name == "output":
                os.mkdir(inPath + "\\output")
            elif name == "intermediate":
                os.mkdir(inPath + "\\intermediate")
            else:
                print("Error: missing expected folder " + name + " at given path " + inPath)
                output = False
            
    return output

def overlayColors(filename ,inputPath, outputPath, color):
    #background = Image.open(inputPath + filename)
    #foreground = Image.open("test2.png")

    #Image.alpha_composite(background, foreground).save("test3.png")
    return

def main():
    parser = argparse.ArgumentParser(description='pack two sets of textures in seperate texture sheets where one set maps on to the other [named outlines/ and colors/]')
    parser.add_argument('-p', '--path', default="", dest='path', type=str, help="Change target location for outlines/ and colors/ folders")
    parser.add_argument('-n', '--normals', default=False, dest='normalsEnabled', type=bool, help="Enable the generation of normal map using the colors generated from output")
    parser.add_argument('-s', '--smooth', default=0., type=float, help='requires --normals smooth gaussian blur applied on the image')
    parser.add_argument('-it', '--intensity', default=1., type=float, help='requires --normals intensity of the normal map')

    inputFolderNames = ["outlines", "colors", "masks"]
    args = parser.parse_args()
    if(not verifyFolderStructure(args.path, inputFolderNames)):
        print("Failed to verify folder structure, aborting.")
        return

    filePathList = pack(args.path,inputFolderNames) #this should create a temp folder
    #invert outlines & put it on a black background
    #put the colors & on a black background
    #make temp variant of the colors where all transparent pixels are black & all opaque pixels are white
    #generate normals using the temp variant
    NormalMapGen.generateNormals("colors", args.path, "\\intermediate\\", "\\output\\", args.smooth, args.intensity)
    #put masks on a black background

if __name__ == '__main__':
    main()
