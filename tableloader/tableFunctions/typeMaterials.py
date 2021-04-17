# -*- coding: utf-8 -*-
import sys
import os
from sqlalchemy import Table

from yaml import load
try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")


def importyaml(connection,metadata,sourcePath,language='en'):
    print("Importing Type Materials")
    invTypeMaterials = Table('invTypeMaterials',metadata)
    
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','typeMaterials.yaml'),'r') as yamlstream:
        print("importing {}".format(os.path.basename(yamlstream.name)))
        materials=load(yamlstream,Loader=SafeLoader)
        print("{} loaded".format(os.path.basename(yamlstream.name)))
        for typeid in materials:
            for material in materials[typeid]['materials']:
                connection.execute(invTypeMaterials.insert(),
                            typeID=typeid,
                            materialTypeID=material.get('materialTypeID'),
                            quantity=material.get('quantity', 0)
                )
    trans.commit()
