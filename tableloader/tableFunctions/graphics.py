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
    eveGraphics = Table('eveGraphics',metadata)
    print("Importing Graphics")
    with open(os.path.join(sourcePath,'fsd','graphicIDs.yaml')) as yamlstream:
        print(f"importing {os.path.basename(yamlstream.name)}")
        trans = connection.begin()
        graphics=load(yamlstream,Loader=SafeLoader)
        print(f"{os.path.basename(yamlstream.name)} loaded")
        for graphic in graphics:
            connection.execute(eveGraphics.insert().values(
                            graphicID=graphic,
                            sofFactionName=graphics[graphic].get('sofFactionName',''),
                            graphicFile=graphics[graphic].get('graphicFile',''),
                            sofHullName=graphics[graphic].get('sofHullName',''),
                            sofRaceName=graphics[graphic].get('sofRaceName',''),
                            description=graphics[graphic].get('description','')))
    trans.commit()
