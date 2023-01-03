import WoTBModelsDowngrader as Downgrader
import LoggerErrors as Logger
import BinaryFile as BinFile
import KeyedArchive

TYPE_NONE           =  0
TYPE_BOOLEAN        =  1
TYPE_INT32          =  2
TYPE_FLOAT          =  3
TYPE_STRING         =  4
TYPE_WIDE_STRING    =  5
TYPE_BYTE_ARRAY     =  6
TYPE_UINT32         =  7
TYPE_KEYED_ARCHIVE  =  8
TYPE_INT64          =  9
TYPE_UINT64         = 10
TYPE_VECTOR2        = 11
TYPE_VECTOR3        = 12
TYPE_VECTOR4        = 13
TYPE_MATRIX2        = 14
TYPE_MATRIX3        = 15
TYPE_MATRIX4        = 16
TYPE_COLOR          = 17
TYPE_FASTNAME       = 18
TYPE_AABBOX3        = 19
TYPE_FILEPATH       = 20
TYPE_FLOAT64        = 21
TYPE_INT8           = 22
TYPE_UINT8          = 23
TYPE_INT16          = 24
TYPE_UINT16         = 25
TYPE_RECT           = 26
TYPE_VARIANT_VECTOR = 27
TYPE_QUANTERION     = 28
TYPE_TRANSFORM      = 29
TYPE_AABBOX2        = 30
TYPES_COUNT         = 31

def AsString(byteArray):
    return bytes([TYPE_STRING]) + len(byteArray).to_bytes(4, 'little') + byteArray

def AsInt32(number):
    if type(number) == int:
        return bytes([TYPE_INT32]) + number.to_bytes(4, 'little')
    elif type(number) == bytes:
        return bytes([TYPE_INT32]) + number
    else:
        Logger.Error("Wrong number type:", type(number))

def AsKeyedArchive(byteArray):
    return bytes([TYPE_KEYED_ARCHIVE]) + len(byteArray).to_bytes(4, 'little') + byteArray

def Read(stream, dictionaryRes = None):

    varType = int.from_bytes(stream.read(1), 'little')
    data = None

    if varType == TYPE_STRING:
        if dictionaryRes != None:
            stringRes = KeyedArchive.GetByteArrayFromKeyHash(dictionaryRes, stream.read(4))
            data = len(stringRes).to_bytes(4, 'little') + stringRes
        else:
            stringLenB = stream.read(4)
            stringAsBytes = stream.read(int.from_bytes(stringLenB, 'little'))
            data = stringLenB + stringAsBytes

    elif varType == TYPE_BOOLEAN:
        data = stream.read(1)

    elif varType == TYPE_INT32:
        data = stream.read(4)

    elif varType == TYPE_FLOAT:
        data = stream.read(4)

    elif varType == TYPE_BYTE_ARRAY:
        sizeOfArrayB = stream.read(4)
        sizeOfArray = int.from_bytes(sizeOfArrayB, 'little')
        data = sizeOfArrayB + stream.read(sizeOfArray)
        
    elif varType == TYPE_UINT32:
        data = stream.read(4)

    elif varType == TYPE_KEYED_ARCHIVE:
        oldArchiveSize = stream.read(4)
        stringMap = KeyedArchive.Load(stream, dictionaryRes)
        archive = KeyedArchive.CreateArchiveFromStringMap(stringMap)
        data = len(archive).to_bytes(4, 'little') + archive

    elif varType == TYPE_INT64:
        data = stream.read(8)

    elif varType == TYPE_UINT64:
        data = stream.read(8)

    elif varType == TYPE_VECTOR2:
        data = stream.read(8)

    elif varType == TYPE_VECTOR3:
        data = stream.read(12)

    elif varType == TYPE_VECTOR4:
        data = stream.read(16)

    elif varType == TYPE_MATRIX2:
        data = stream.read(16)

    elif varType == TYPE_MATRIX3:
        data = stream.read(36)

    elif varType == TYPE_MATRIX4:
        data = stream.read(64)

    elif varType == TYPE_COLOR:
        data = stream.read(16)

    elif varType == TYPE_FASTNAME:
        if dictionaryRes != None:
            fastNameRes = KeyedArchive.GetByteArrayFromKeyHash(dictionaryRes, stream.read(4))
            data = len(fastNameRes).to_bytes(4, 'little') + fastNameRes
        else:
            fastNameLenB = stream.read(4)
            fastName = stream.read(int.from_bytes(fastNameLenB, 'little'))
            data = fastNameLenB + fastName

    elif varType == TYPE_AABBOX3:
        data = stream.read(24)

    elif varType == TYPE_FLOAT64:
        data = stream.read(8)

    elif varType == TYPE_INT8:
        data = stream.read(1)

    elif varType == TYPE_UINT8:
        data = stream.read(1)

    elif varType == TYPE_INT16:
        data = stream.read(2)

    elif varType == TYPE_UINT16:
        data = stream.read(2)

    elif varType == TYPE_RECT:
        data = stream.read(16)

    elif varType == TYPE_VARIANT_VECTOR:
        data = stream.read(4)
        variantNum = int.from_bytes(data, 'little')
        for k in range (variantNum):
            if dictionaryRes != None:
                data += Read(stream, dictionaryRes)
            else:
                data += Read(stream)
    
    elif varType == TYPE_QUANTERION:
        data = stream.read(16)

    elif varType == TYPE_TRANSFORM:
        data = stream.read(24 + 16) # 2 * VECTOR3 + 1 * QUANTERION

    elif varType == TYPE_AABBOX2:
        data = stream.read(16)

    else:
        Logger.Error("WRONG TYPE FOUND, PLEASE ADD IT:", [varType, stream.tell()])

    return varType.to_bytes(1, 'little') + data

def GetVariantVector(keyToFind, stream, dictionaryRes = None):
    if dictionaryRes != None:
        keyToFind = KeyedArchive.GetKeyHashFromByteArray(dictionaryRes, keyToFind)

    EOF = BinFile.GetEOF(stream)
    currPos = stream.tell()
    while stream.read(len(keyToFind)) != keyToFind:
        if currPos == EOF:
            Logger.Error("DVASSERT: TYPE_VARIANT_VECTOR EOF")
        currPos += 1
        stream.seek(currPos)

    variantTypeList = []
    if BinFile.ReadInt(stream, 1) != TYPE_VARIANT_VECTOR:
        Logger.Error("DVASSERT: TYPE_VARIANT_VECTOR")

    variantNum = BinFile.ReadInt(stream, 4)
    for k in range(variantNum):
        variantType = Read(stream, dictionaryRes)
        variantTypeList.append(variantType)
    return variantTypeList
