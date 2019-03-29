# -*- coding: utf-8 -*-

import os

from utils import yaml_stream

from sqlalchemy import Table

def load(connection, metadata, sourcePath):

    eveIcons = Table('eveIcons',metadata)
    print("Importing Icons")

    trans = connection.begin()

    with open(os.path.join(sourcePath,'fsd','groupIDs.yaml'),'r') as yamlstream:
        for icon in yaml_stream.read_by_any(yamlstream):
            for icon_id, icon_details in icon.items():
                connection.execute(eveIcons.insert(),
                                iconID=icon_id,
                                iconFile=icon_details.get('iconFile',''),
                                description=icon_details.get('description',''))
    trans.commit()
