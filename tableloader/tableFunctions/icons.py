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
    eveIcons = Table('eveIcons',metadata)
    print("Importing Icons")
    with open(os.path.join(sourcePath,'fsd','iconIDs.yaml'),'r') as yamlstream:
        print("importing {}".format(os.path.basename(yamlstream.name)))
        trans = connection.begin()
        icons=load(yamlstream,Loader=SafeLoader)
        print("{} loaded".format(os.path.basename(yamlstream.name)))
        for icon in icons:
            connection.execute(eveIcons.insert(),
                            iconID=icon,
                            iconFile=icons[icon].get('iconFile',''),
                            description=icons[icon].get('description',''))
    trans.commit()
