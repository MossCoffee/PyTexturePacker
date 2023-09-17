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
import shutil
import json
from PIL import Image, ImageColor, ImageFilter
import PIL.ImageOps
from enum import Enum

class Mode(Enum):
    CLASSIC=0
    SKETCH_ONLY=1
    SKETCH_AND_FINAL=2
    MISMATCH=3

def pack(targetDirectory, inputFolderNames, padding,):
    packer = Packer.create(max_width=4096, max_height=4096,trim_mode=1,inner_padding=padding,enable_rotated=False)
    return packer.packWithMatchingUVs(inputFolderNames, "intermediate", "output", targetDirectory)

def newFolderInput():
    print("Where is your root folder?")
    print("Path: >> <FOLDER_ROOT> << /<character_name>/<animation_name>")
    path = queryInput()
    print("\n")
    print("Path: "+ path +"/ >> <CHARACTER_NAME> << /<animation_name>")
    print("What character is this for?")
    characterName = queryInput()
    print("\n")
    print("Path: "+ path +"/"+ characterName +"/ >> <ANIMATION_NAME> <<")
    print("What is the name of your animation?")
    animationName = queryInput()
    print("\n")
    print("~~ Final Path: "+ path +"/"+ characterName +"/" + animationName + " ~~")
    return path, characterName, animationName

def validatePicturesInFolders(path):
    mode = Mode.MISMATCH 
    sketchAssets = ["sketches"]
    sketchAssetCount = 0
    finalArtAssets = ["colors", "lines", "masks"]
    finalArtAssetCount = 0
    
    scanPath = os.scandir(path=path)

    for folder_name in sketchAssets:
        hasValidFolders = False
        for file in scanPath:
            if file.is_dir() and file.name == folder_name:
                hasValidFolders = True

        if not hasValidFolders:
            #This is likely a legacy folder structure, return 0
            break

        folderPath = path + "/" + folder_name
        scanPath = os.scandir(path=folderPath)
        currentFolderAssetCount = 0
        
        for file in scanPath:
            if file.is_file():
                currentFolderAssetCount += 1
        if(sketchAssetCount != currentFolderAssetCount and sketchAssetCount != 0):
            print("Error in validating sketch assests, you have a uneven amount of them! You shouldn't be hitting this. Aborting.")
            return mode
        else:
            sketchAssetCount = currentFolderAssetCount

    for folder_name in finalArtAssets:
        folderPath = path + "/" + folder_name
        scanPath = os.scandir(path=folderPath)
        currentFolderAssetCount = 0
        for file in scanPath:
            if file.is_file():
                currentFolderAssetCount += 1
        if(finalArtAssetCount != currentFolderAssetCount and finalArtAssetCount != 0):
            print("Error in validating final assests, you have different amounts of assets in each folder! Aborting.")
            return
        else:
            finalArtAssetCount = currentFolderAssetCount
    
    if sketchAssetCount > 0 and finalArtAssetCount > 0 and sketchAssetCount == finalArtAssetCount:
        mode = Mode.SKETCH_AND_FINAL
    elif sketchAssetCount > 0 and finalArtAssetCount == 0:
        mode = Mode.SKETCH_ONLY
    elif sketchAssetCount == 0 and finalArtAssetCount > 0:
        mode = Mode.CLASSIC
    else: 
        mode = Mode.MISMATCH
    
    return mode

def copyImportFile(path, characterName, animationName):
    #copy over a modfied version of the settings file, with the name & characterName changed
    shutil.copy(os.getcwd() + "/resources/import.json", path + "/output/import.json")
    modifySettingsFile(path + "/output/import.json", animationName, characterName)
    print("Successfully Regenerated Import File")

def regenerateImportFile():
    path, characterName, animationName = newFolderInput()
    copyImportFile(path + "/" + characterName + "/" + animationName, characterName, animationName)

def newFolderFlow():
    path, characterName, animationName = newFolderInput()

    neededFiles = ["sketches", "colors", "lines", "masks","output","intermediate"]
    scanPath = os.scandir(path=path)
    hasValidFolder = False
    for file in scanPath:
        if file.is_dir() and file.name == characterName:
            hasValidFolder = True

    if not hasValidFolder:
        os.mkdir(path + "/" + characterName)

    path = path + "/" + characterName

    scanPath = os.scandir(path=path)
    hasValidFolder = False
    for file in scanPath:
        if file.is_dir() and file.name == characterName:
            hasValidFolder = True

    if not hasValidFolder:
        os.mkdir(path + "/" + animationName)

    path = path + "/" + animationName
    scanPath = os.scandir(path=path)

    for file in scanPath:
        if file.is_dir():
            for dirName in neededFiles:
                if file.name == dirName:
                    neededFiles.remove(dirName)
                    break
    
    if len(neededFiles) > 0:
        for dirName in neededFiles:
            os.mkdir(path + "/" + dirName)
    
    copyImportFile(path, characterName, animationName)

    print("Folder set up complete!")
    print("Once you've populated the folders, run the command:")
    print("\tmain.py -p=\"" + path + "\"")
    print("To pack the textures!")
    return

def modifySettingsFile(settingsFilePath, animationName, characterName):
    #load the file 
    file = open(settingsFilePath, "r")
    if file == None:
        print("Error opening import file. Aborting.")
        return
    jsonBlob = json.load(file)
    file.close()
    #overwrite "name" with animationName
    #jsonBlob["name"] = animationName
    jsonBlob["animationName"] = animationName
    #overwrite "characterName" with characterName
    #jsonBlob["characterName"] = characterName
    jsonBlob["characterName"] = characterName
    #save file
    file = open(settingsFilePath, "w")
    if file == None:
        print("Error opening import file. Aborting.")
        return
    json.dump(jsonBlob, file)
    file.close()
    return

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

def CreateSolidImageColorUsingBase(filename, workingDir, outputFilename=None, outputDir=None, color="black"):
    if outputFilename is None:
        outputFilename = filename
    if outputDir is None:
        outputDir = workingDir
    background = Image.open(workingDir + filename + ".png")
    foreground = Image.new(background.mode, background.size, color) #color defaults to black

    Image.alpha_composite(background, foreground).save(outputDir + outputFilename + ".png")
    return


def createNormalMapBase(*filenames, workingDir, outputFilename=None, outputDir=None):
    if outputDir is None:
        outputDir = workingDir
    foreground = None
    for file in filenames:
        current_image = Image.open(workingDir + file + ".png")
        if foreground == None:
            foreground = current_image
        else:
            foreground = Image.alpha_composite(current_image, foreground)
    
    background = Image.new(foreground.mode, foreground.size, "white")

    maskedImage = Image.composite(background, foreground, foreground)
    maskBackground = Image.new(maskedImage.mode, maskedImage.size, "black")
    Image.alpha_composite(maskBackground, maskedImage).save(outputDir + outputFilename + ".png")
    return

def createMask(LinesFilename, MasksFilename, ColorsFilename, workingDir, outputFilename=None, outputDir=None):
    if outputFilename is None:
        outputFilename = MasksFilename
    if outputDir is None:
        outputDir = workingDir
    
    #Step 1 apply masks_png to solid blue background
    masks_png = Image.open(workingDir + MasksFilename + ".png")
    background = Image.new(masks_png.mode, masks_png.size, (0,0,255)) #Mask shadow color go here
    masksOnBackground = Image.alpha_composite(background, masks_png)
    
    colors_png = Image.open(workingDir + ColorsFilename + ".png")
    lines_png = Image.open(workingDir + LinesFilename + ".png")
    colorsAndLines = Image.alpha_composite(colors_png, lines_png)
    #Step 3 mask the combo to the color combo
    

    FinalMask = Image.composite(masksOnBackground, colorsAndLines, colorsAndLines)
    #Step 3, but that on a black background
    outputBackground = Image.new(masks_png.mode, masks_png.size, "black")
    Image.alpha_composite(outputBackground, FinalMask).save(outputDir + MasksFilename + ".png")
    return

def queryInput(validInputs=None, errorString=None):
    output = ""
    hasValidInput = False
    while not hasValidInput:
        inputVal = input()
        if validInputs == None:
            output = inputVal
            hasValidInput = True
            break
        else:
            inputVal = inputVal.capitalize()

        if not inputVal in validInputs:
            if(errorString != None):
                print("Invalid Input, please try again.")
            else:
                print(errorString)
        else:
            output = inputVal
            hasValidInput = True 
    return output

def ClassicPackingMode(path,inputFolderNames,args):
    #Packing
    filePathList = pack(path,inputFolderNames,args.padding)

    intermediateFilePath = path + "\\intermediate\\"
    outputFilePath = path + "\\output\\"

    #Lines
    #add a white background to the lines
    fillAlphaWithColor("lines", intermediateFilePath, outputFilename="lines_background", color="white")
    #invert the image
    invertImage("lines_background", intermediateFilePath, outputFilename="lines", outputDir=outputFilePath)
    #Colors
    fillAlphaWithColor("colors", intermediateFilePath, outputDir=outputFilePath)
    #Masks
    createMask("lines","masks", "colors", intermediateFilePath, outputDir=outputFilePath)
    #Normals
    #make temp variant of the colors where all transparent pixels are black & all opaque pixels are white
    createNormalMapBase("colors", "masks", "lines", workingDir=intermediateFilePath, outputFilename="normal_map_base")
    #generate normals using the temp variant
    NormalMapGen.generateNormals("normal_map_base", path, "\\intermediate\\", "\\output\\", args.smooth, args.intensity)
    #normal map blur
    normal_map= Image.open(outputFilePath + "normals.png")
    blurImage = normal_map.filter(ImageFilter.GaussianBlur(15))
    blurImage.save(outputFilePath + "normals.png")
    return

def SketchesOnlyPackingMode(path, inputFolderNames, args):
    #Packing
    filePathList = pack(path,inputFolderNames,args.padding)

    sketchesFilePath = path + "\\sketches\\"
    intermediateFilePath = path + "\\intermediate\\"
    outputFilePath = path + "\\output\\"

    #Lines
    #add a white background to the lines
    fillAlphaWithColor("sketches", intermediateFilePath, outputFilename="lines_background", color="white")
    #invert the image
    invertImage("lines_background", intermediateFilePath, outputFilename="lines", outputDir=outputFilePath)
    #Colors

    #Create an RGB image with an all white background
    CreateSolidImageColorUsingBase("sketches", intermediateFilePath, outputFilename="colors" ,outputDir=outputFilePath,color="white")
    #Masks
    #Create an All Blue RGB Image 
    CreateSolidImageColorUsingBase("sketches", intermediateFilePath, outputFilename="masks" ,outputDir=outputFilePath,color="blue")
    #createMask("sketches","sketches", "sketches", intermediateFilePath, outputDir=outputFilePath)
    #Normals
    #Make a solid image with RGBA color (129,129,255,255)
    #make temp variant of the colors where all transparent pixels are black & all opaque pixels are white
    #createNormalMapBase("sketches", "sketches", "sketches", workingDir=intermediateFilePath, outputFilename="normal_map_base")
    CreateSolidImageColorUsingBase("sketches", intermediateFilePath, outputFilename="normals" ,outputDir=outputFilePath,color=(129,129,255))
    #generate normals using the temp variant
    #NormalMapGen.generateNormals("normal_map_base", path, "\\intermediate\\", "\\output\\", args.smooth, args.intensity)
    return


def main():
    parser = argparse.ArgumentParser(description='|| VivSpriteTexturePacker || Texture Packer for the VivSprite art pipeline. Use this command line by typing \"python3 main.py [optional arguments]" in your current directory. By default, the texture packer will run all steps. This can take a lot of time, and will throw away all existing work. If you want to run fewer steps, then specify the steps you want to run by passing the corresponding flag.')
    parser.add_argument('-p', '--path', default="", dest='path', type=str, help="\"-p=\"C:\\path\"\" to use - Sets the working directory")
    #Toggle steps options
    #parser.add_argument('-v', '--verify', default=False, dest='verify', type=bool, help="\"-v=True\" to enable - Enables the verify packing step")
    #parser.add_argument('-pk', '--packing', default=False, dest='packing', type=bool, help="\"-pk=True\" to enable - Enables the texture packing step")
    #parser.add_argument('-l', '--lines', default=False, dest='lines', type=bool, help="\"-o=True\" to enable - Enables the lines processing step")
    #parser.add_argument('-c', '--colors', default=False, dest='colors', type=bool, help="\"-c=True\" to enable - Enables the colors processing step")
    #parser.add_argument('-m', '--masks', default=False, dest='masks', type=bool, help="\"-m=True\" to enable - Enables the masks processing step")
    #parser.add_argument('-n', '--normals', default=False, dest='normals', type=bool, help="\"-n=True\" to enable - Enable the generation of normal map using the colors generated from output")
    #normals options
    parser.add_argument('-s', '--smooth', default=3., type=float, help='\"-s=3\" to use - Set smooth gaussian blur applied on the image')
    parser.add_argument('-it', '--intensity', default=6., type=float, help='\"-it=6.0\" to use - Set Intensity of the normal map')
    #packing options 
    parser.add_argument('-pad', '--padding', default=2, dest='padding', type=int, help='\"-pad=3\" to use - Set the padding in between each texture when packing')
    inputFolderNames = ["lines", "colors", "masks"]
    args = parser.parse_args()
    
    path = args.path
    if not args.path:
        print("No path given, do you want to use the new folder flow? Y/N")
        userInput = queryInput(["Y", "N"], "Please input either Y to confirm or N to cancel")
        if(userInput == "Y"):
            newFolderFlow()
            exit()
        print("Do you want to regenerate an Import.json file? Y/N")
        userInput = queryInput(["Y", "N"], "Please input either Y to confirm or N to cancel")
        if(userInput == "Y"):
            regenerateImportFile()
            exit()
        print("Do you want to specify the path now? Y/N")
        userInput = queryInput(["Y", "N"], "Please input either Y to confirm or N to cancel")
        if(userInput == "Y"):
            path = queryInput()
        else:
            print("Please specify the path when running this tool using the -p parameter.")
            print("Quitting")
            exit()

    if(not verifyFolderStructure(path, inputFolderNames)):
        print("Failed to verify folder structure, aborting.")
        return
    processingMode = validatePicturesInFolders(path=path)
    if(processingMode == Mode.MISMATCH):
        print("Expected number of images in lines, masks and colors to be equal. sketches should be equal or 0. Aborting.")
        return
    
    if processingMode == Mode.SKETCH_ONLY:
        print("Running packer in Sketch only mode...")
        inputFolderNames.insert(0, "sketches")
        SketchesOnlyPackingMode(path=path, inputFolderNames=inputFolderNames, args=args)
        return
    elif processingMode == Mode.SKETCH_AND_FINAL:
        print("Running packer in Sketch and Final Art mode...")
        inputFolderNames.insert(0, "sketches")
        ClassicPackingMode(path=path, inputFolderNames=inputFolderNames, args=args)
        return
    elif processingMode == Mode.CLASSIC:
        print("Running packer in Classic mode...")
        ClassicPackingMode(path=path, inputFolderNames=inputFolderNames, args=args)
        return
    else:
        assert(False)

if __name__ == '__main__':
    main()
