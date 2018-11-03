# -*- coding: utf-8 -*-
import os
from sqlalchemy import Table
from yaml import load

try:
	from yaml import CSafeLoader as SafeLoader
	print("Using CSafeLoader")
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")

def importyaml(connection,metadata,sourcePath):
    eveIcons = Table('eveIcons',metadata)
    print("Importing Icons")
    print("Opening Yaml")
    with open(os.path.join(sourcePath,'fsd','iconIDs.yaml'),'r') as yamlstream:
        trans = connection.begin()
        icons=load(yamlstream,Loader=SafeLoader)
        print("Yaml Processed into memory")
        for icon in icons:
            connection.execute(eveIcons.insert(),
                            iconID=icon,
                            iconFile=icons[icon].get('iconFile',''),
                            description=icons[icon].get('description',''))
    trans.commit()
