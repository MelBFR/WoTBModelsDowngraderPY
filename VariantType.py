import BinaryFile as BinFile
import KeyedArchive as KeyedArchive
import LoggerErrors as Logger
import WoTBModelsDowngrader as Downgrader

def AsString(byteArray):
    return bytes([Downgrader.TYPE_STRING]) + len(byteArray).to_bytes(4, 'little') + byteArray

def AsInt32(number):
    if type(number) == int:
        return bytes([Downgrader.TYPE_INT32]) + number.to_bytes(4, 'little')
    elif type(number) == bytes:
        return bytes([Downgrader.TYPE_INT32]) + number
    else:
        Logger.Error("Wrong number type:", type(number))

def AsKeyedArchive(byteArray):
    return bytes([Downgrader.TYPE_KEYED_ARCHIVE]) + len(byteArray).to_bytes(4, 'little') + byteArray

def Read(stream, dictionaryRes = None):

    varType = int.from_bytes(stream.read(1), 'little')
    data = None

    if varType == Downgrader.TYPE_STRING:
        if dictionaryRes != None:
            stringRes = Downgrader.GetByteArrayFromKeyHash(dictionaryRes, stream.read(4))
            data = len(stringRes).to_bytes(4, 'little') + stringRes
        else:
            stringLenB = stream.read(4)
            stringAsBytes = stream.read(int.from_bytes(stringLenB, 'little'))
            data = stringLenB + stringAsBytes

    elif varType == Downgrader.TYPE_BOOLEAN:
        data = stream.read(1)

    elif varType == Downgrader.TYPE_INT32:
        data = stream.read(4)

    elif varType == Downgrader.TYPE_FLOAT:
        data = stream.read(4)

    elif varType == Downgrader.TYPE_BYTE_ARRAY:
        sizeOfArrayB = stream.read(4)
        sizeOfArray = int.from_bytes(sizeOfArrayB, 'little')
        data = sizeOfArrayB + stream.read(sizeOfArray)
        
    elif varType == Downgrader.TYPE_UINT32:
        data = stream.read(4)

    elif varType == Downgrader.TYPE_KEYED_ARCHIVE:
        oldArchiveSize = stream.read(4)
        stringMap = KeyedArchive.Load(stream, dictionaryRes)
        archive = KeyedArchive.CreateArchiveFromStringMap(stringMap)
        data = len(archive).to_bytes(4, 'little') + archive

    elif varType == Downgrader.TYPE_INT64:
        data = stream.read(8)

    elif varType == Downgrader.TYPE_UINT64:
        data = stream.read(8)

    elif varType == Downgrader.TYPE_VECTOR2:
        data = stream.read(8)

    elif varType == Downgrader.TYPE_VECTOR3:
        data = stream.read(12)

    elif varType == Downgrader.TYPE_VECTOR4:
        data = stream.read(16)

    elif varType == Downgrader.TYPE_MATRIX2:
        data = stream.read(16)

    elif varType == Downgrader.TYPE_MATRIX3:
        data = stream.read(36)

    elif varType == Downgrader.TYPE_MATRIX4:
        data = stream.read(64)

    elif varType == Downgrader.TYPE_COLOR:
        data = stream.read(16)

    elif varType == Downgrader.TYPE_FASTNAME:
        if dictionaryRes != None:
            fastNameRes = Downgrader.GetByteArrayFromKeyHash(dictionaryRes, stream.read(4))
            data = len(fastNameRes).to_bytes(4, 'little') + fastNameRes
        else:
            fastNameLenB = stream.read(4)
            fastName = stream.read(int.from_bytes(fastNameLenB, 'little'))
            data = fastNameLenB + fastName

    elif varType == Downgrader.TYPE_AABBOX3:
        data = stream.read(24)

    elif varType == Downgrader.TYPE_FLOAT64:
        data = stream.read(8)

    elif varType == Downgrader.TYPE_INT8:
        data = stream.read(1)

    elif varType == Downgrader.TYPE_UINT8:
        data = stream.read(1)

    elif varType == Downgrader.TYPE_INT16:
        data = stream.read(2)

    elif varType == Downgrader.TYPE_UINT16:
        data = stream.read(2)

    elif varType == Downgrader.TYPE_VARIANT_VECTOR:
        data = stream.read(4)
        variantNum = int.from_bytes(data, 'little')
        for k in range (variantNum):
            if dictionaryRes != None:
                data += Read(stream, dictionaryRes)
            else:
                data += Read(stream)
    
    else:
        Logger.Error("WRONG TYPE FOUND, PLEASE ADD IT:", [varType, stream.tell()])

    return varType.to_bytes(1, 'little') + data

def GetVariantVector(keyToFind, stream, dictionaryRes = None):
    if dictionaryRes != None:
        keyToFind = Downgrader.GetKeyHashFromByteArray(dictionaryRes, keyToFind)

    EOF = BinFile.GetEOF(stream)
    currPos = stream.tell()
    while stream.read(len(keyToFind)) != keyToFind:
        if currPos == EOF:
            Logger.Error("DVASSERT: TYPE_VARIANT_VECTOR EOF")
        currPos += 1
        stream.seek(currPos)

    variantTypeList = []
    if BinFile.ReadInt(stream, 1) != Downgrader.TYPE_VARIANT_VECTOR:
        Logger.Error("DVASSERT: TYPE_VARIANT_VECTOR")

    variantNum = BinFile.ReadInt(stream, 4)
    for k in range(variantNum):
        variantType = Read(stream, dictionaryRes)
        variantTypeList.append(variantType)
    return variantTypeList
