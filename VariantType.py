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

def Read(sc2Stream, dictionaryRes = None, isNode = False):

    varTypeB = sc2Stream.read(1)
    varType = int.from_bytes(varTypeB, 'little')
    data = None

    if varType == Downgrader.TYPE_STRING:
        if dictionaryRes != None:
            stringRes = Downgrader.GetByteArrayFromKeyHash(dictionaryRes, sc2Stream.read(4))
            data = len(stringRes).to_bytes(4, 'little') + stringRes
        else:
            stringLenB = sc2Stream.read(4)
            stringAsBytes = sc2Stream.read(int.from_bytes(stringLenB, 'little'))
            data = stringLenB + stringAsBytes

    elif varType == Downgrader.TYPE_BOOLEAN:
        data = sc2Stream.read(1)

    elif varType == Downgrader.TYPE_INT32:
        data = sc2Stream.read(4)

    elif varType == Downgrader.TYPE_FLOAT:
        data = sc2Stream.read(4)

    elif varType == Downgrader.TYPE_BYTE_ARRAY:
        sizeOfArrayB = sc2Stream.read(4)
        sizeOfArray = int.from_bytes(sizeOfArrayB, 'little')
        data = sizeOfArrayB + sc2Stream.read(sizeOfArray)
        
    elif varType == Downgrader.TYPE_UINT32:
        data = sc2Stream.read(4)

    elif varType == Downgrader.TYPE_KEYED_ARCHIVE:
        oldArchiveSize = sc2Stream.read(4)
        if dictionaryRes != None:
            stringMap = KeyedArchive.Load(sc2Stream, dictionaryRes)
        else:
            stringMap = KeyedArchive.Load(sc2Stream)

        hierarchyData = None
        if Downgrader.HIERARCHY_SUPPORT:
            for eachObjMap in stringMap:
                if AsString(b"#hierarchy") in eachObjMap:
                    hierarchyData = eachObjMap[1]
                    eachObjMap[0] = AsString(b"#childrenCount")
                    eachObjMap[1] = AsInt32(eachObjMap[1][1:5])
        data = KeyedArchive.CreateArchiveFromStringMap(stringMap, isNode)
        if hierarchyData != None:
            mem = BinFile.WriteBufferForLoadData("child.bin", hierarchyData)
            mem.read(1)
            for k in range(BinFile.ReadInt(mem, 4)):
                mem.read(1)
                data += mem.read(BinFile.ReadInt(mem, 4))
            mem.close()

    elif varType == Downgrader.TYPE_INT64:
        data = sc2Stream.read(8)

    elif varType == Downgrader.TYPE_UINT64:
        data = sc2Stream.read(8)

    elif varType == Downgrader.TYPE_VECTOR2:
        data = sc2Stream.read(8)

    elif varType == Downgrader.TYPE_VECTOR3:
        data = sc2Stream.read(12)

    elif varType == Downgrader.TYPE_VECTOR4:
        data = sc2Stream.read(16)

    elif varType == Downgrader.TYPE_MATRIX2:
        data = sc2Stream.read(16)

    elif varType == Downgrader.TYPE_MATRIX3:
        data = sc2Stream.read(36)

    elif varType == Downgrader.TYPE_MATRIX4:
        data = sc2Stream.read(64)

    elif varType == Downgrader.TYPE_COLOR:
        data = sc2Stream.read(16)

    elif varType == Downgrader.TYPE_FASTNAME:
        if dictionaryRes != None:
            fastNameRes = Downgrader.GetByteArrayFromKeyHash(dictionaryRes, sc2Stream.read(4))
            data = len(fastNameRes).to_bytes(4, 'little') + fastNameRes
        else:
            fastNameLenB = sc2Stream.read(4)
            fastName = sc2Stream.read(int.from_bytes(fastNameLenB, 'little'))
            data = fastNameLenB + fastName

    elif varType == Downgrader.TYPE_AABBOX3:
        data = sc2Stream.read(24)

    elif varType == Downgrader.TYPE_FLOAT64:
        data = sc2Stream.read(8)

    elif varType == Downgrader.TYPE_FILEPATH:
        Logger.Error("TYPE_FILEPATH is Disabled", varType)

    elif varType == Downgrader.TYPE_INT8:
        data = sc2Stream.read(1)

    elif varType == Downgrader.TYPE_UINT8:
        data = sc2Stream.read(1)

    elif varType == Downgrader.TYPE_INT16:
        data = sc2Stream.read(2)

    elif varType == Downgrader.TYPE_UINT16:
        data = sc2Stream.read(2)

    elif varType == Downgrader.TYPE_UNKNOWN:
        Logger.Error("TYPE_UNKNOWN is Disabled", varType)

    elif varType == Downgrader.TYPE_VARIANT_VECTOR:
        data = sc2Stream.read(4)
        variantNum = int.from_bytes(data, 'little')
        for k in range (variantNum):
            if dictionaryRes != None:
                data += Read(sc2Stream, dictionaryRes)
            else:
                data += Read(sc2Stream)
    
    else:
        Logger.Error("WRONG TYPE FOUND, PLEASE ADD IT:", varType)

    if not isNode:
        return varTypeB + data
    return data

def GetVariantVector(keyToFind, sc2Stream, dictionaryRes = None):
    if dictionaryRes != None:
        keyToFind = Downgrader.GetKeyHashFromByteArray(dictionaryRes, keyToFind)

    EOF = BinFile.GetEOF(sc2Stream)
    currPos = sc2Stream.tell()
    while sc2Stream.read(len(keyToFind)) != keyToFind:
        if currPos == EOF:
            Logger.Error("DVASSERT: TYPE_VARIANT_VECTOR EOF")
        currPos += 1
        sc2Stream.seek(currPos)

    variantTypeList = []
    if BinFile.ReadInt(sc2Stream, 1) != Downgrader.TYPE_VARIANT_VECTOR:
        Logger.Error("DVASSERT: TYPE_VARIANT_VECTOR")

    variantNum = BinFile.ReadInt(sc2Stream, 4)
    for k in range(variantNum):
        variantTypeList.append(Read(sc2Stream, dictionaryRes, True))
    return variantTypeList
