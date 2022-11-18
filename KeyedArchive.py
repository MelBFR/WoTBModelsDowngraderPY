import BinaryFile as BinFile
import LoggerErrors as Logger
import VariantType as VariantType
import WoTBModelsDowngrader as Downgrader

def LoadRegisteredArchive(stream):
    # In case of Dictionary Archives
    archiveSignature = stream.read(2)
    if archiveSignature != b'KA':
        Logger.Error("Wrong Archive Signature:", archiveSignature)

    archiveVersion = BinFile.ReadInt(stream, 2)
    archiveItemNum = BinFile.ReadInt(stream, 4)
    if archiveItemNum == 0:
        Logger.Error("Wrong Archive ItemsCount:", archiveItemNum)

    if archiveVersion != 0x0002:
        Logger.Error("Wrong Dictionary Version:", archiveVersion)
        
    dictionaryKeys = []
    dictionaryHash = []
    for i in range(archiveItemNum):
        stringLen = BinFile.ReadInt(stream, 2)
        dictionaryKeys.append(stream.read(stringLen))

    for i in range(archiveItemNum):
        dictionaryHash.append(stream.read(4))
    
    return [dictionaryKeys, dictionaryHash]

# While Downgrading Models, Only StringMap Exists !
# So we Return a StringMap Version of Keyed Archive
def Load(stream, dictionaryRes = None):
    archiveSignature = stream.read(2)
    if archiveSignature != b'KA':
        Logger.Error("Wrong Archive Signature:", archiveSignature)

    stringMapArchive = []

    # In case of Empty Archives
    archiveVersion = BinFile.ReadInt(stream, 2)
    if archiveVersion == 0xFF02:
        return stringMapArchive

    # In case of Others Archives
    archiveItemNum = BinFile.ReadInt(stream, 4)
    if archiveItemNum == 0:
        Logger.Error("Wrong Archive ItemsCount:", archiveItemNum)

    # In case of Hashed Strings Archives
    if archiveVersion == 0x0102:
        for i in range(archiveItemNum):
            variantKey = Downgrader.GetByteArrayFromKeyHash(dictionaryRes, stream.read(4))
            variantKey = VariantType.AsString(variantKey)
            variantObj = VariantType.Read(stream, dictionaryRes)
            stringMapArchive.append([variantKey, variantObj])

        return stringMapArchive

    # In case of StringMap Archives
    if archiveVersion == 0x0001:
        for i in range(archiveItemNum):
            variantKey = VariantType.Read(stream, dictionaryRes)
            variantObj = VariantType.Read(stream, dictionaryRes)
            stringMapArchive.append([variantKey, variantObj])

        return stringMapArchive
        
    Logger.Error("Wrong Archive Version:", archiveVersion, stream.tell())

def CreateArchiveFromStringMap(stringMap):
    archive = b'KA'+(0x0001).to_bytes(2, 'little')+len(stringMap).to_bytes(4, 'little')
    for k in range(len(stringMap)):
        archive += stringMap[k][0] + stringMap[k][1]
    return archive

def RemoveArchiveTypeAndSize(archive):
    archive = archive[-len(archive) + 5:]
    return archive

def GetArchivesFromVariantVector(variantVector):
    for i in range(len(variantVector)):
        variantVector[i] = RemoveArchiveTypeAndSize(variantVector[i])
    return variantVector
