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
    print("Importing controlTowerResources")
    invControlTowerResources = Table('invControlTowerResources',metadata)
    
    print("opening Yaml")
        
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','controlTowerResources.yaml'),'r') as yamlstream:
        print("importing")
        controlTowerResources=load(yamlstream,Loader=SafeLoader)
        print("Yaml Processed into memory")
        for controlTowerResourcesid in controlTowerResources:
            for purpose in controlTowerResources[controlTowerResourcesid]['resources']:
                connection.execute(invControlTowerResources.insert(),
                                controlTowerTypeID=controlTowerResourcesid,
                                resourceTypeID=purpose['resourceTypeID'],
                                purpose=purpose['purpose'],
                                quantity=purpose.get('quantity',0),
                                minSecurityLevel=purpose.get('minSecurityLevel',None),
                                factionID=purpose.get('factionID',None)
                )
    trans.commit()
