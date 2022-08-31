from LoggerErrors import *
from BinaryReader import *

sc2File = "ST_B1.sc2"
scgFile = "ST_B1.scg"

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
TYPE_UNKNOWN        = 26
TYPE_VARIANT_VECTOR = 27
TYPES_COUNT         = 28

SCENE_FILE_CURRENT_VERSION = 40
SCENE_FILE_MINIMAL_VERSION = 30

def GetKeyHashFromByteArray(dictionaryRes, byteArray):
    return dictionaryRes[1][dictionaryRes[0].index(byteArray)]
def GetByteArrayFromKeyHash(dictionaryRes, keyHash):
    return dictionaryRes[0][dictionaryRes[1].index(keyHash)]

def TryReadGeometryFile(scgStream):
    headerSignature = scgStream.read(4)
    if headerSignature != b'SCPG':
        LoggerErrorV("Wrong HeaderGeom Signature", headerSignature)
        
    headerVersion = ReadInt(scgStream, 4)
    if headerVersion != 1:
        LoggerErrorV("Wrong HeaderGeom Version != 1", headerVersion)

    headerPolyNum = ReadInt(scgStream, 4)
    if headerPolyNum != ReadInt(scgStream, 4):
        LoggerError("Wrong HeaderGeom Number of PolygonGroup Nodes")

    polygonGroups = scgStream.read()
    return polygonGroups

def ReadSCG(scgStream):
    return TryReadGeometryFile(scgStream)

def TryReadSceneHeader(sc2Stream):
    headerSignature = sc2Stream.read(4)
    if headerSignature != b'SFV2':
        LoggerErrorV("Wrong Header Signature:", headerSignature)
        
    headerVersion = ReadInt(sc2Stream, 4)
    if headerVersion > SCENE_FILE_CURRENT_VERSION:
        LoggerErrorV("Unsupported:", SCENE_FILE_CURRENT_VERSION)
    elif headerVersion < SCENE_FILE_MINIMAL_VERSION:
        LoggerErrorV("Unsupported:", SCENE_FILE_MINIMAL_VERSION)

    headerNodeNum = ReadInt(sc2Stream, 4)
    if headerNodeNum == 0:
        LoggerError("Wrong Number of Hierarchy Nodes == 0")

    return headerNodeNum

def TryReadDescriptor(sc2Stream):
    return sc2Stream.read(24)

def TryReadDictionary(sc2Stream):
    archiveSignature = sc2Stream.read(2)
    if archiveSignature != b'KA':
        LoggerError("Wrong Dictionary Archive Signature")

    archiveVersion = ReadInt(sc2Stream, 2)
    if archiveVersion != 0x0002:
        LoggerError("Wrong Dictionary Archive Version")

    archiveItemsCount = ReadInt(sc2Stream, 4)
    if archiveItemsCount == 0:
        LoggerError("Dictionary Archive is Empty == 0")

    dictionaryKeys = []
    dictionaryHash = []

    for i in range(archiveItemsCount):
        stringLen = ReadInt(sc2Stream, 2)
        dictionaryKeys.append(sc2Stream.read(stringLen))

    for i in range(archiveItemsCount):
        dictionaryHash.append(sc2Stream.read(4))
    
    return [dictionaryKeys, dictionaryHash]

def TryReadVariantVector(keyToFind, dictionaryRes, sc2Stream):
    keyHash = GetKeyHashFromByteArray(dictionaryRes, keyToFind)
    currPos = sc2Stream.tell()

    while sc2Stream.read(4) != keyHash:
        currPos += 1
        sc2Stream.seek(currPos)

    varType = ReadInt(sc2Stream, 1)
    if varType != TYPE_VARIANT_VECTOR:
        LoggerErrorV("Wrong Type Found:", varType)

    itemsCount = ReadInt(sc2Stream, 4)

def ReadSC2(sc2Stream):
    headerNodeNum = TryReadSceneHeader(sc2Stream)
    descriptorBuf = TryReadDescriptor(sc2Stream)
    dictionaryRes = TryReadDictionary(sc2Stream)

    dataNodesList = TryReadVariantVector(b"#dataNodes", dictionaryRes, sc2Stream)
    return True

def DowngradeModel():
    scgStream = open(scgFile, "rb+")
    sc2Stream = open(sc2File, "rb+")
    
    polygonGroups = ReadSCG(scgStream)
    returnedValue = ReadSC2(sc2Stream)

DowngradeModel()
