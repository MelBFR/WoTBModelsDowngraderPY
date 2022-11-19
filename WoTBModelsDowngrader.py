import BinaryFile as BinFile
import KeyedArchive as KeyedArchive
import LoggerErrors as Logger
import VariantType as VariantType
import HierarchySystem as Hierarchy

sc2File = "M-6-Y.sc2"
scgFile = sc2File.replace(".sc2", ".scg")
outFile = sc2File.replace(".sc2", "_res.sc2")

# Feature to Support new Hierarchy on Olders ResourceEditor
# If Enabled, Instead of storing all nodes in Variant Vectors
# We count number of childrens and place nodes right after
HIERARCHY_SUPPORT = True
# Feature to Support new ParticleEmitterNodes by deleting them
# It needs to be enabled at the same time of HIERARCHY_SUPPORT
# Basically to also remove the ParticleEffectComponent component
PARTICLES_SUPPORT = True

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
TYPE_QUATERNION     = 28
TYPE_TRANSFORM      = 29
TYPES_COUNT         = 30

SCENE_FILE_CURRENT_VERSION = 43
SCENE_FILE_MINIMAL_VERSION = 30
SCENE_FILE_REBUILD_VERSION = 24

DESCRIPTOR_BUFFER = bytes([0x4b, 0x41, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

def GetKeyHashFromByteArray(dictionaryRes, byteArray):
    return dictionaryRes[1][dictionaryRes[0].index(byteArray)]
def GetByteArrayFromKeyHash(dictionaryRes, keyHash):
    return dictionaryRes[0][dictionaryRes[1].index(keyHash)]

def TryReadGeometryFile(stream):
    headerSignature = stream.read(4)
    if headerSignature != b'SCPG':
        Logger.Error("Wrong HeaderGeom Signature", headerSignature)
        
    headerVersion = BinFile.ReadInt(stream, 4)
    if headerVersion != 1:
        Logger.Error("Wrong HeaderGeom Version != 1", headerVersion)

    headerPolyNum = BinFile.ReadInt(stream, 4)
    if headerPolyNum != BinFile.ReadInt(stream, 4):
        Logger.Error("Wrong HeaderGeom Number of PolygonGroup Nodes")

    polygonGroups = stream.read()
    return polygonGroups

def ReadSCG(stream):
    return TryReadGeometryFile(stream)

def TryReadSceneHeader(stream):
    headerSignature = stream.read(4)
    if headerSignature != b'SFV2':
        Logger.Error("Wrong Header Signature:", headerSignature)
        
    headerVersion = BinFile.ReadInt(stream, 4)
    if headerVersion > SCENE_FILE_CURRENT_VERSION:
        Logger.Error("Unsupported:", SCENE_FILE_CURRENT_VERSION)
    elif headerVersion < SCENE_FILE_MINIMAL_VERSION:
        Logger.Error("Unsupported:", SCENE_FILE_MINIMAL_VERSION)

    headerNodeNum = BinFile.ReadInt(stream, 4)
    if headerNodeNum == 0:
        Logger.Error("Wrong Number of Hierarchy Nodes == 0")

    return headerNodeNum

def TryReadDescriptor(stream):
    return stream.read(24)

def ReadSC2(stream):
    headerNodeNum = TryReadSceneHeader(stream)
    descriptorBuf = TryReadDescriptor(stream)
    dictionaryRes = KeyedArchive.LoadRegisteredArchive(stream)

    dataNodes = VariantType.GetVariantVector(b"#dataNodes", stream, dictionaryRes)
    dataNodes = KeyedArchive.GetArchivesFromVariantVector(dataNodes)

    hierarchy = VariantType.GetVariantVector(b"#hierarchy", stream, dictionaryRes)
    hierarchy = KeyedArchive.GetArchivesFromVariantVector(hierarchy)

    return [dataNodes, hierarchy]

def CreateSceneFile(outStream, receivedNodes, polygonGroups = None):
    if PARTICLES_SUPPORT:
        for eachNode in receivedNodes[0].copy():
            if VariantType.AsString(b"ParticleEmitterNode") in eachNode:
                receivedNodes[0].remove(eachNode)

    dataNodesNum = len(receivedNodes[0])
    if polygonGroups != None:
        dataNodesNum += polygonGroups.count(b"PolygonGroup")
        
    outStream.write(b"SFV2")
    outStream.write(SCENE_FILE_REBUILD_VERSION.to_bytes(4, 'little'))
    outStream.write(len(receivedNodes[1]).to_bytes(4, 'little'))
    outStream.write(DESCRIPTOR_BUFFER)
    outStream.write(dataNodesNum.to_bytes(4, 'little'))

    if polygonGroups != None:
        outStream.write(polygonGroups)
    # dataNodes
    for eachNode in receivedNodes[0]:
        outStream.write(eachNode)
    # hierarchy
    for eachNode in receivedNodes[1]:
        if HIERARCHY_SUPPORT:
            eachNode = Hierarchy.TransformNewToOldHierarchy(eachNode)
        outStream.write(eachNode)
    outStream.close()

def DowngradeModel():
    
    sc2Stream, scgStream, polygonGroups, receivedNodes = None, None, None, None

    if BinFile.IsPathExists(sc2File):
        sc2Stream = open(sc2File, "rb+")
        receivedNodes = ReadSC2(sc2Stream)
        
    if BinFile.IsPathExists(scgFile):
        scgStream = open(scgFile, "rb+")
        polygonGroups = ReadSCG(scgStream)

    if sc2File == None:
        Logger.Error("Downgrade failed to open file", sc2File)
    
    outStream = open(outFile, "wb")
    CreateSceneFile(outStream, receivedNodes, polygonGroups)
    
if __name__ == '__main__':
    DowngradeModel()
