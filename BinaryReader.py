def ReadInt(stream, size):
    return int.from_bytes(stream.read(size), 'little')

def GetEOF(stream):
    currentPos = stream.tell()
    stream.seek(-1, 2)
    EOF = stream.tell()
    stream.seek(currentPos, 0)
    return EOF