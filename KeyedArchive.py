import BinaryReader as BinReader
import LoggerErrors as Logger
import VariantType as VariantType
import WoTBModelsDowngrader as Downgrader

def LoadDictionary(sc2Stream):
    # In case of Dictionary Archives
    archiveSignature = sc2Stream.read(2)
    if archiveSignature != b'KA':
        Logger.Error("Wrong Archive Signature:", archiveSignature)

    archiveVersion = BinReader.ReadInt(sc2Stream, 2)
    archiveItemNum = BinReader.ReadInt(sc2Stream, 4)
    if archiveItemNum == 0:
        Logger.Error("Wrong Archive ItemsCount:", archiveItemNum)

    if archiveVersion != 0x0002:
        Logger.Error("Wrong Dictionary Version:", archiveVersion)
        
    dictionaryKeys = []
    dictionaryHash = []
    for i in range(archiveItemNum):
        stringLen = BinReader.ReadInt(sc2Stream, 2)
        dictionaryKeys.append(sc2Stream.read(stringLen))

    for i in range(archiveItemNum):
        dictionaryHash.append(sc2Stream.read(4))
    
    return [dictionaryKeys, dictionaryHash]

def Load(sc2Stream, dictionaryRes):
    archiveSignature = sc2Stream.read(2)
    if archiveSignature != b'KA':
        Logger.Error("Wrong Archive Signature:", archiveSignature)

    # In case of Empty Archives
    archiveVersion = BinReader.ReadInt(sc2Stream, 2)
    if archiveVersion == 0xFF02:
        return True

    # In case of Others Archives
    archiveItemNum = BinReader.ReadInt(sc2Stream, 4)
    if archiveItemNum == 0:
        Logger.Error("Wrong Archive ItemsCount:", archiveItemNum)

    # In case of Hashed Strings Archives
    if archiveVersion == 0x0102:
        # While Downgrading Models, Only StringMap Exists !
        # So we Return a StringMap Version of Keyed Archive
        stringMapArchive = []
        for i in range(archiveItemNum):
            variantKey = Downgrader.GetByteArrayFromKeyHash(dictionaryRes, sc2Stream.read(4))
            # ByteArray(Str) -> VariantType ByteArray(Str)
            variantKey = bytes([Downgrader.TYPE_STRING]) + len(variantKey).to_bytes(4, 'little') + variantKey
            variantObj = VariantType.Read(sc2Stream, dictionaryRes)
            stringMapArchive.append([variantKey, variantObj])

        return stringMapArchive

    # In case of StringMap Archives
    if archiveVersion == 0x0001:
        stringMapArchive = []
        for i in range(archiveItemNum):
            variantKey = VariantType.Read(sc2Stream, dictionaryRes)
            variantObj = VariantType.Read(sc2Stream, dictionaryRes)
            stringMapArchive.append([variantKey, variantObj])

        return stringMapArchive

    