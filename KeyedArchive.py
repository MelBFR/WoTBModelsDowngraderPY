from LoggerErrors import*
from BinaryReader import*
from WoTBModelsDowngrader import*

def TryReadDictionaryArchive(sc2Stream):
    # In case of Dictionary Archives
    archiveSignature = sc2Stream.read(2)
    if archiveSignature != b'KA':
        LoggerError("Wrong Archive Signature:", archiveSignature)

    archiveVersion = ReadInt(sc2Stream, 2)
    archiveItemNum = ReadInt(sc2Stream, 4)
    if archiveItemNum == 0:
        LoggerErrorV("Wrong Archive ItemsCount:", archiveItemNum)

    if archiveVersion != 0x0002:
        LoggerErrorV("Wrong Dictionary Version:", archiveVersion)
        
    dictionaryKeys = []
    dictionaryHash = []
    for i in range(archiveItemNum):
        stringLen = ReadInt(sc2Stream, 2)
        dictionaryKeys.append(sc2Stream.read(stringLen))

    for i in range(archiveItemNum):
        dictionaryHash.append(sc2Stream.read(4))
    
    return [dictionaryKeys, dictionaryHash]

def KeyedArchiveLoad(sc2Stream, dictionaryRes):
    archiveSignature = sc2Stream.read(2)
    if archiveSignature != b'KA':
        LoggerError("Wrong Archive Signature:", archiveSignature)

    # In case of Empty Archives
    archiveVersion = ReadInt(sc2Stream, 2)
    if archiveVersion == 0xFF02:
        return True

    # In case of Others Archives
    archiveItemNum = ReadInt(sc2Stream, 4)
    if archiveItemNum == 0:
        LoggerErrorV("Wrong Archive ItemsCount:", archiveItemNum)

    # In case of Hashed Strings Archives
    if archiveVersion == 0x0102:
        # While Downgrading Models, Only StringMap Exists !
        # So we Return a StringMap Version of Keyed Archive
        stringMapArchive = []
        for i in range(archiveItemNum):
            variantKey = GetByteArrayFromKeyHash(sc2Stream.read(4), dictionaryRes)
            variantObj = VariantTypeRead(sc2Stream, dictionaryRes)
            stringMapArchive.append([variantKey, variantObj])

        return stringMapArchive

    # In case of StringMap Archives
    if archiveVersion == 0x0001:
        stringMapArchive = []
        for i in range(archiveItemNum):
            variantKey = VariantTypeRead(sc2Stream, dictionaryRes)
            variantObj = VariantTypeRead(sc2Stream, dictionaryRes)
            stringMapArchive.append([variantKey, variantObj])

        return stringMapArchive

    