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
    eveIcons = Table('eveIcons',metadata)
    print("Importing Icons")
    with open(os.path.join(sourcePath,'fsd','iconIDs.yaml')) as yamlstream:
        print(f"importing {os.path.basename(yamlstream.name)}")
        trans = connection.begin()
        icons=load(yamlstream,Loader=SafeLoader)
        print(f"{os.path.basename(yamlstream.name)} loaded")
        for icon in icons:
            connection.execute(eveIcons.insert().values(
                            iconID=icon,
                            iconFile=icons[icon].get('iconFile',''),
                            description=icons[icon].get('description','')))
    trans.commit()
