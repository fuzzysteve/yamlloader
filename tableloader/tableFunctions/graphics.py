# -*- coding: utf-8 -*-
import os
import yaml
from sqlalchemy import Table



def importyaml(connection,metadata,sourcePath):
    eveGraphics = Table('eveGraphics',metadata)
    print("Importing Graphics")
    print("opening Yaml")
    with open(os.path.join(sourcePath,'fsd','graphicIDs.yaml'),'r') as yamlstream:
        print("importing")
        trans = connection.begin()
        graphics=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
        print("Yaml Processed into memory")
        for graphic in graphics:
            connection.execute(eveGraphics.insert(),
                            graphicID=graphic,
                            sofFactionName=graphics[graphic].get('sofFactionName',''),
                            graphicFile=graphics[graphic].get('graphicFile',''),
                            sofHullName=graphics[graphic].get('sofHullName',''),
                            sofRaceName=graphics[graphic].get('sofRaceName',''),
                            description=graphics[graphic].get('description',''))
    trans.commit()
