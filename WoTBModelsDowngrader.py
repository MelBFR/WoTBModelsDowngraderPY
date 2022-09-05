import BinaryReader as BinReader
import KeyedArchive as KeyedArchive
import LoggerErrors as Logger
import VariantType as VariantType

sc2File = "ST_B1.sc2"
scgFile = sc2File.replace(".sc2", ".scg")
outFile = sc2File.replace(".sc2", "_res.sc2")

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
SCENE_FILE_REBUILD_VERSION = 24

DESCRIPTOR_BUFFER = bytes([0x4b, 0x41, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

def GetKeyHashFromByteArray(dictionaryRes, byteArray):
    return dictionaryRes[1][dictionaryRes[0].index(byteArray)]
def GetByteArrayFromKeyHash(dictionaryRes, keyHash):
    return dictionaryRes[0][dictionaryRes[1].index(keyHash)]

def TryReadGeometryFile(scgStream):
    headerSignature = scgStream.read(4)
    if headerSignature != b'SCPG':
        Logger.Error("Wrong HeaderGeom Signature", headerSignature)
        
    headerVersion = BinReader.ReadInt(scgStream, 4)
    if headerVersion != 1:
        Logger.Error("Wrong HeaderGeom Version != 1", headerVersion)

    headerPolyNum = BinReader.ReadInt(scgStream, 4)
    if headerPolyNum != BinReader.ReadInt(scgStream, 4):
        Logger.Error("Wrong HeaderGeom Number of PolygonGroup Nodes")

    polygonGroups = scgStream.read()
    return polygonGroups

def ReadSCG(scgStream):
    return TryReadGeometryFile(scgStream)

def TryReadSceneHeader(sc2Stream):
    headerSignature = sc2Stream.read(4)
    if headerSignature != b'SFV2':
        Logger.Error("Wrong Header Signature:", headerSignature)
        
    headerVersion = BinReader.ReadInt(sc2Stream, 4)
    if headerVersion > SCENE_FILE_CURRENT_VERSION:
        Logger.Error("Unsupported:", SCENE_FILE_CURRENT_VERSION)
    elif headerVersion < SCENE_FILE_MINIMAL_VERSION:
        Logger.Error("Unsupported:", SCENE_FILE_MINIMAL_VERSION)

    headerNodeNum = BinReader.ReadInt(sc2Stream, 4)
    if headerNodeNum == 0:
        Logger.Error("Wrong Number of Hierarchy Nodes == 0")

    return headerNodeNum

def TryReadDescriptor(sc2Stream):
    return sc2Stream.read(24)

def TryReadVariantVector(keyToFind, dictionaryRes, sc2Stream):
    keyHash = GetKeyHashFromByteArray(dictionaryRes, keyToFind)
    currPos = sc2Stream.tell()

    while sc2Stream.read(4) != keyHash:
        currPos += 1
        sc2Stream.seek(currPos)

    variantTypeList = []

    # Storing as a List instead of BytesArray
    if BinReader.ReadInt(sc2Stream, 1) != TYPE_VARIANT_VECTOR:
        Logger.Error("DVASSERT: TYPE_VARIANT_VECTOR")

    variantNum = BinReader.ReadInt(sc2Stream, 4)
    for k in range(variantNum):
        variantTypeList.append(VariantType.Read(sc2Stream, dictionaryRes))

    return variantTypeList

def ReadSC2(sc2Stream):
    headerNodeNum = TryReadSceneHeader(sc2Stream)
    descriptorBuf = TryReadDescriptor(sc2Stream)
    dictionaryRes = KeyedArchive.LoadDictionary(sc2Stream)

    dataNodesList = TryReadVariantVector(b"#dataNodes", dictionaryRes, sc2Stream)
    hierarchyList = TryReadVariantVector(b"#hierarchy", dictionaryRes, sc2Stream)

    return [dataNodesList, hierarchyList]

def CreateSceneHeader(outStream, receivedNodes):
    outStream.write(b"SFV2" + SCENE_FILE_REBUILD_VERSION.to_bytes(4, 'little'))
    outStream.write(len(receivedNodes[1]).to_bytes(4, 'little') + DESCRIPTOR_BUFFER)

def CreateSceneFile(receivedNodes, polygonGroups):
    outStream = open(outFile, "wb")
    CreateSceneHeader(outStream, receivedNodes)
    dataNodesNum = len(receivedNodes[0]) + polygonGroups.count(b"PolygonGroup")
    outStream.write(dataNodesNum.to_bytes(4, 'little'))

    outStream.write(polygonGroups)
    for eachNode in receivedNodes[0]:
        outStream.write(eachNode)
    for eachNode in receivedNodes[1]:
        outStream.write(eachNode)
    outStream.close()

def DowngradeModel():
    scgStream = open(scgFile, "rb+")
    sc2Stream = open(sc2File, "rb+")
    
    polygonGroups = ReadSCG(scgStream)
    receivedNodes = ReadSC2(sc2Stream)

    CreateSceneFile(receivedNodes, polygonGroups)

if __name__ == '__main__':
    DowngradeModel()
