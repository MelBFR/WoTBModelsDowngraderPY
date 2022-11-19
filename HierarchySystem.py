import WoTBModelsDowngrader as Downgrader
import KeyedArchive as KeyedArchive
import VariantType as VariantType
import LoggerErrors as Logger
import BinaryFile as BinFile

HIERARCHY_KEY = b"#hierarchy"
CHILDRENS_KEY = b"#childrenCount"
PARTICLES_KEY = b"ParticleEffectComponent"

def TransformNewToOldHierarchy(nodeArchive):
    if Downgrader.PARTICLES_SUPPORT and PARTICLES_KEY in nodeArchive:
        nodeArchive = RemoveSpecificComponentFromNode(nodeArchive, PARTICLES_KEY)

    if HIERARCHY_KEY in nodeArchive:
        stringMap = KeyedArchive.CreateStringMapFromArchive(nodeArchive)
        hierarchyVariantVectorBytes = KeyedArchive.GetVariantInStringMap(stringMap, HIERARCHY_KEY)
        hierarchyVariantVectorCount = int.from_bytes(hierarchyVariantVectorBytes[1:5], 'little')
        if not hierarchyVariantVectorBytes:
            Logger.Error("StringMap #hierarchy key not found")
        
        # Remove Hierarchy VariantVector + Add Parameter ChildrenCount Int32
        stringMap = KeyedArchive.RemoveKeysInStringMap(stringMap, HIERARCHY_KEY)
        stringMap = KeyedArchive.SetVariantInStringMap(stringMap, CHILDRENS_KEY, VariantType.AsInt32(hierarchyVariantVectorCount))

        # Transform and Add Childrens Nodes After Current Node Recursively
        nodeArchive = KeyedArchive.CreateArchiveFromStringMap(stringMap)
        mem = BinFile.WriteBufferForLoadData(hierarchyVariantVectorBytes)
        mem.read(5)
        for i in range(hierarchyVariantVectorCount):
            childArchive = KeyedArchive.RemoveArchiveTypeAndSize(VariantType.Read(mem))
            childArchive = TransformNewToOldHierarchy(childArchive)
            nodeArchive += childArchive

    return nodeArchive

def RemoveSpecificComponentFromNode(nodeArchive, compTypename):
    if PARTICLES_KEY in nodeArchive:
        compsVar = GetComponentsVariantFromNode(nodeArchive)
        compsArch = KeyedArchive.RemoveArchiveTypeAndSize(compsVar)
        compsList = GetEachComponentsList(compsArch)

        # Removing the Component if found
        isFound = False
        for eachComponent in compsList.copy():
            if not compTypename in eachComponent:
                continue
            compsList.remove(eachComponent)
            isFound = True
        
        # It means it's in #hierarchy variantVector
        if not isFound:
            return nodeArchive

        serializedCompsList = SetEachComponentsList(compsList)
        newCompsArch = KeyedArchive.CreateArchiveFromStringMap(serializedCompsList)
        newCompsVar = VariantType.AsKeyedArchive(newCompsArch)
        nodeArchive = nodeArchive.replace(compsVar, newCompsVar)

    return nodeArchive

        
def GetComponentsVariantFromNode(nodeArchive):
    stringMap = KeyedArchive.CreateStringMapFromArchive(nodeArchive)
    compsVar = KeyedArchive.GetVariantInStringMap(stringMap, b"components")
    return compsVar

def GetEachComponentsList(compsArch):
    numberOfComps = compsArch.count(b"comp.typename")

    compsArchMap = KeyedArchive.CreateStringMapFromArchive(compsArch)
    listOfComps = []
    for i in range(numberOfComps):
        # 1-> "0001" / 20-> "0020" as bytes
        indexComp = str(i).zfill(4).encode()
        component = KeyedArchive.GetVariantInStringMap(compsArchMap, indexComp)
        listOfComps.append(component)

    return listOfComps

def SetEachComponentsList(listOfComps):
    numberOfComps = len(listOfComps)
    compsArchMap = []
    for i in range(numberOfComps):
        # 1-> "0001" / 20-> "0020" as bytes
        indexComp = str(i).zfill(4).encode()
        compsArchMap.append([indexComp, listOfComps[i]])
    return compsArchMap