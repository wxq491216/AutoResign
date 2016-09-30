import os
import shutil

def isFile(path):
    if os.path.isfile(path):
        return True
    else:
        return False

def hasFile(folder, fileName):
    result = False
    if not os.path.exists(folder) or os.path.isfile(folder):
        return result

    for file in os.listdir(folder):
        filePath = os.path.join(folder, file)
        if os.path.isfile(filePath):
            if file == fileName:
                result = True
                break
    return result

def removeDir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)

def removeFile(file):
    if os.path.exists(file):
        os.remove(file)

def copyDir(sourceDir, targetDir):
    if sourceDir.find(".svn") > 0:
        return
    for file in os.listdir(sourceDir):
        sourceFile = os.path.join(sourceDir, file)
        targetFile = os.path.join(targetDir, file)
        if os.path.isfile(sourceFile):
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            if not os.path.exists(targetFile) or (os.path.exists(targetFile) and (os.path.getsize(targetFile) != os.path.getsize(sourceFile))):
                shutil.copyfile(sourceFile, targetFile)
        if os.path.isdir(sourceFile):
            copyDir(sourceFile, targetFile)

def copyFile(source, target):
    if not os.path.isfile(source):
        return
    shutil.copyfile(source, target)