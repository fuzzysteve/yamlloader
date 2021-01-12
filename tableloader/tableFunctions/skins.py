# -*- coding: utf-8 -*-
from yaml import load, dump
try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")

import os
import sys
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
        print("importing {}".format(os.path.basename(yamlstream.name)))
        skins=load(yamlstream,Loader=SafeLoader)
        print("{} loaded".format(os.path.basename(yamlstream.name)))
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
        print("importing {}".format(os.path.basename(yamlstream.name)))
        skinlicenses=load(yamlstream,Loader=SafeLoader)
        print("{} loaded".format(os.path.basename(yamlstream.name)))
        for licenseid in skinlicenses:
            connection.execute(skinLicense.insert(),
                                licenseTypeID=licenseid,
                                duration=skinlicenses[licenseid]['duration'],
                                skinID=skinlicenses[licenseid]['skinID'])
    print("opening Yaml3")
    with open(os.path.join(sourcePath,'fsd','skinMaterials.yaml'),'r') as yamlstream:
        print("importing {}".format(os.path.basename(yamlstream.name)))
        skinmaterials=load(yamlstream,Loader=SafeLoader)
        print("{} loaded".format(os.path.basename(yamlstream.name)))
        for materialid in skinmaterials:
            connection.execute(skinMaterials.insert(),
                                skinMaterialID=materialid,
                                displayNameID=skinmaterials[materialid]['displayNameID'],
                                materialSetID=skinmaterials[materialid]['materialSetID']
                                )

    trans.commit()
