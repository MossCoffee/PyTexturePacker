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
from PIL import Image
from PIL import ImageColor
import PIL.ImageOps   



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

def invertImage(filename, workingDir, outputFilename=None, outputDir=None):
    if outputFilename is None:
        outputFilename = filename
    if outputDir is None:
        outputDir = workingDir
    image = Image.open(workingDir + filename + ".png")
    inverted_image = PIL.ImageOps.invert(image.convert(mode="RGB"))

    inverted_image.save(outputDir + outputFilename + ".png")
    return

def fillAlphaWithColor(filename, workingDir, outputFilename=None, outputDir=None, color="black"):
    if outputFilename is None:
        outputFilename = filename
    if outputDir is None:
        outputDir = workingDir
    foreground = Image.open(workingDir + filename + ".png")
    background = Image.new(foreground.mode, foreground.size, color) #color defaults to black

    Image.alpha_composite(background, foreground).save(outputDir + outputFilename + ".png")
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
    intermediateFilePath = args.path + "\\intermediate\\"
    outputFilePath = args.path + "\\output\\"

    #invert outlines & put it on a black background
    fillAlphaWithColor("outlines", intermediateFilePath, outputFilename="outlines_background", color="white")
    invertImage("outlines_background", intermediateFilePath, outputFilename="outlines", outputDir=outputFilePath)
    #put the colors & on a black background
    fillAlphaWithColor("colors", intermediateFilePath, outputDir=outputFilePath)
    fillAlphaWithColor("masks", intermediateFilePath, outputDir=outputFilePath)
    #make temp variant of the colors where all transparent pixels are black & all opaque pixels are white
    #generate normals using the temp variant
    NormalMapGen.generateNormals("colors", args.path, "\\output\\", "\\output\\", args.smooth, args.intensity)
    #put masks on a black background

if __name__ == '__main__':
    main()
