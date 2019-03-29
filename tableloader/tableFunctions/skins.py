# -*- coding: utf-8 -*-
import os

from utils import yaml_stream

from sqlalchemy import Table

def load(connection, metadata, sourcePath):

    skinLicense   = Table('skinLicense',metadata)
    skinMaterials = Table('skinMaterials',metadata)
    skins_table   = Table('skins',metadata)
    skinShip      = Table('skinShip',metadata)

    trans = connection.begin()
    print("Importing Skins")

    with open(os.path.join(sourcePath,'fsd','skins.yaml'),'r') as yamlstream:
        for skin in yaml_stream.read_by_any(yamlstream):
            for skin_id, skin_details in skin.items():
                connection.execute(skins_table.insert(),
                                skinID=skin_id,
                                internalName=skin_details.get('internalName',''),
                                skinMaterialID=skin_details.get('skinMaterialID',''))
                for ship in skin_details['types']:
                    connection.execute(skinShip.insert(),
                                    skinID=skin_id,
                                    typeID=ship)

    print("opening Yaml2")
    with open(os.path.join(sourcePath,'fsd','skinLicenses.yaml'),'r') as yamlstream:
        for skin_license in yaml_stream.read_by_any(yamlstream):
            for skin_license_id, skin_license_details in skin_license.items():
                connection.execute(skinLicense.insert(),
                                    licenseTypeID=skin_license_id,
                                    duration=skin_license_details['duration'],
                                    skinID=skin_license_details['skinID'])
    print("opening Yaml3")
    with open(os.path.join(sourcePath,'fsd','skinMaterials.yaml'),'r') as yamlstream:
        for skin_material in yaml_stream.read_by_any(yamlstream):
            for skin_material_id, skin_material_details in skin_material.items():
                connection.execute(skinMaterials.insert(),
                                    skinMaterialID=skin_material_id,
                                    displayNameID=skin_material_details['displayNameID'],
                                    materialSetID=skin_material_details['materialSetID']
                                    )

    trans.commit()
