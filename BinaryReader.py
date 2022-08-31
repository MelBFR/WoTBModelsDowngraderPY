def ReadInt(stream, size):
    return int.from_bytes(stream.read(size), 'little')