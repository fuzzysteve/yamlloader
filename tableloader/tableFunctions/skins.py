# -*- coding: utf-8 -*-
import os
import yaml
from sqlalchemy import Table

def importyaml(connection,metadata,sourcePath):
    skinLicense = Table('skinLicense',metadata)
    skinMaterials = Table('skinMaterials',metadata)
    skins_table = Table('skins',metadata)
    skinShip = Table('skinShip',metadata)            
                
    trans = connection.begin()
    print("Importing Skins")
    print("opening Yaml1")
    with open(os.path.join(sourcePath,'fsd','skins.yaml'),'r') as yamlstream:
        skins=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
        print("Yaml Processed into memory")
        for skinid in skins:
            connection.execute(skins_table.insert(),
                            skinID=skinid,
                            internalName=skins[skinid].get('internalName',''),
                            skinMaterialID=skins[skinid].get('skinMaterialID',''))
            for ship in skins[skinid]['types']:
                connection.execute(skinShip.insert(),
                                skinID=skinid,
                                typeID=ship)


    print("opening Yaml2")
    with open(os.path.join(sourcePath,'fsd','skinLicenses.yaml'),'r') as yamlstream:
        skinlicenses=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
        print("Yaml Processed into memory")
        for licenseid in skinlicenses:
            connection.execute(skinLicense.insert(),
                                licenseTypeID=licenseid,
                                duration=skinlicenses[licenseid]['duration'],
                                skinID=skinlicenses[licenseid]['skinID'])
    print("opening Yaml3")
    with open(os.path.join(sourcePath,'fsd','skinMaterials.yaml'),'r') as yamlstream:
        skinmaterials=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
        print("Yaml Processed into memory")
        for materialid in skinmaterials:
            connection.execute(skinMaterials.insert(),
                                skinMaterialID=materialid,
                                displayNameID=skinmaterials[materialid]['displayNameID'],
                                materialSetID=skinmaterials[materialid]['materialSetID']
                                )

    trans.commit()
