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

def createNormalMapBase(filename, workingDir, outputFilename=None, outputDir=None):
    if outputFilename is None:
        outputFilename = filename
    if outputDir is None:
        outputDir = workingDir
    
    foreground = Image.open(workingDir + filename + ".png")
    background = Image.new(foreground.mode, foreground.size, "white")

    maskedImage = Image.composite(background, foreground, foreground)
    maskBackground = Image.new(maskedImage.mode, maskedImage.size, "black")
    Image.alpha_composite(maskBackground, maskedImage).save(outputDir + outputFilename + ".png")
    return

def main():
    parser = argparse.ArgumentParser(description='|| VivSpriteTexturePacker || Texture Packer for the VivSprite art pipeline. Use this command line by typing \"python3 main.py [optional arguments]" in your current directory')
    parser.add_argument('-p', '--path', default="", dest='path', type=str, help="\"-p=\"C:\\path\"\" to use - Sets the working directory")
    #Toggle steps options
    parser.add_argument('-v', '--verify', default=False, dest='verify', type=bool, help="\"-v=True\" to enable - Enables the verify packing step")
    parser.add_argument('-pk', '--packing', default=False, dest='packing', type=bool, help="\"-pk=True\" to enable - Enables the texture packing step")
    parser.add_argument('-o', '--outlines', default=False, dest='outlines', type=bool, help="\"-o=True\" to enable - Enables the outlines processing step")
    parser.add_argument('-c', '--colors', default=False, dest='colors', type=bool, help="\"-c=True\" to enable - Enables the colors processing step")
    parser.add_argument('-m', '--masks', default=False, dest='masks', type=bool, help="\"-m=True\" to enable - Enables the masks processing step")
    parser.add_argument('-n', '--normals', default=False, dest='normals', type=bool, help="\"-no=True\" to enable - Enable the generation of normal map using the colors generated from output")
    #normals options
    parser.add_argument('-s', '--smooth', default=0., type=float, help='\"-s=3\" to use - Set smooth gaussian blur applied on the image')
    parser.add_argument('-it', '--intensity', default=1., type=float, help='\"-it=6.0\" to use - Set Intensity of the normal map')

    inputFolderNames = ["outlines", "colors", "masks"]
    args = parser.parse_args()

    allStepsEnabled = not (args.verify or args.packing or args.outlines or args.colors or args.masks or args.normals)

    if allStepsEnabled or args.verify:
        if(not verifyFolderStructure(args.path, inputFolderNames)):
            print("Failed to verify folder structure, aborting.")
            return
    
    if allStepsEnabled or args.packing:
        filePathList = pack(args.path,inputFolderNames)

    intermediateFilePath = args.path + "\\intermediate\\"
    outputFilePath = args.path + "\\output\\"

    if allStepsEnabled or args.outlines:
        #add a white background to the outlines
        fillAlphaWithColor("outlines", intermediateFilePath, outputFilename="outlines_background", color="white")
        #invert the image
        invertImage("outlines_background", intermediateFilePath, outputFilename="outlines", outputDir=outputFilePath)
    if allStepsEnabled or args.colors:
        fillAlphaWithColor("colors", intermediateFilePath, outputDir=outputFilePath)
    if allStepsEnabled or args.masks:
        fillAlphaWithColor("masks", intermediateFilePath, outputDir=outputFilePath)
    if allStepsEnabled or args.normals:
        #make temp variant of the colors where all transparent pixels are black & all opaque pixels are white
        createNormalMapBase("masks", intermediateFilePath, outputFilename="normal_map_base")
        #generate normals using the temp variant
        NormalMapGen.generateNormals("normal_map_base", args.path, "\\intermediate\\", "\\output\\", args.smooth, args.intensity)

if __name__ == '__main__':
    main()
