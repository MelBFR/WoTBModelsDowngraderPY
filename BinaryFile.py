import tempfile
import shutil
import random
import string
import os

def IsPathExists(path):
    return os.path.exists(path)

def DeleteFileFromPath(path):
    if IsPathExists(path):
        os.remove(path)

def DeleteFolderFromPath(path):
    if IsPathExists(path):
        shutil.rmtree(path)

memFolder = tempfile.gettempdir() + "\\mem\\"

def CleanMemFolder():
    DeleteFolderFromPath(memFolder)

def ReadInt(stream, size):
    return int.from_bytes(stream.read(size), 'little')

def GetEOF(stream):
    currentPos = stream.tell()
    stream.seek(-1, 2)
    EOF = stream.tell()
    stream.seek(currentPos, 0)
    return EOF

def GetRandomMemFileName():
    length = 10
    letters = string.ascii_lowercase
    randomFile = ''.join(random.choice(letters) for i in range(length))
    print("GetRandomHierarchyFileName():", randomFile)
    return randomFile

def WriteBufferForLoadData(buffer):
    memFileName = GetRandomMemFileName()
    mem = open(memFolder + memFileName, "wb")
    mem.write(buffer)
    mem = open(memFolder + memFileName, "rb")
    return mem

if IsPathExists(memFolder):
    CleanMemFolder()
os.mkdir(memFolder)