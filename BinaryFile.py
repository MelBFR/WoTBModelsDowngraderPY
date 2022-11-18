import tempfile
import os

def IsPathExists(path):
    return os.path.exists(path)

memFolder = tempfile.gettempdir() + "\\mem\\"
if not IsPathExists(memFolder):
    os.mkdir(memFolder)

def ReadInt(stream, size):
    return int.from_bytes(stream.read(size), 'little')

def GetEOF(stream):
    currentPos = stream.tell()
    stream.seek(-1, 2)
    EOF = stream.tell()
    stream.seek(currentPos, 0)
    return EOF

def WriteBufferForLoadData(memFileName, buffer):
    mem = open(memFolder + memFileName, "wb")
    mem.write(buffer)
    mem = open(memFolder + memFileName, "rb")
    return mem