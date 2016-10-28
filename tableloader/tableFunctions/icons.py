# -*- coding: utf-8 -*-
import os
import yaml
from sqlalchemy import Table


def importyaml(connection,metadata,sourcePath):
    eveIcons = Table('eveIcons',metadata)
    print("Importing Icons")
    print("Opening Yaml")
    with open(os.path.join(sourcePath,'fsd','iconIDs.yaml'),'r') as yamlstream:
        trans = connection.begin()
        icons=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
        print("Yaml Processed into memory")
        for icon in icons:
            connection.execute(eveIcons.insert(),
                            iconID=icon,
                            iconFile=icons[icon].get('iconFile',''),
                            description=icons[icon].get('description',''))
    trans.commit()