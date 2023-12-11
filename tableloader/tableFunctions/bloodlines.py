import sys
import os
#sys.setdefaultencoding("utf-8")
from sqlalchemy import Table

from yaml import load
try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")


def importyaml(connection,metadata,sourcePath,language='en'):
    print("Importing character bloodlines")
    chrBloodlines = Table('chrBloodlines',metadata)
    
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','bloodlines.yaml')) as yamlstream:
        print(f"importing {os.path.basename(yamlstream.name)}")
        bloodlines=load(yamlstream,Loader=SafeLoader)
        print(f"{os.path.basename(yamlstream.name)} loaded")
        for bloodlineid in bloodlines:
            connection.execute(chrBloodlines.insert().values(
                            bloodlineID=bloodlineid,
                            bloodlineName=bloodlines[bloodlineid].get('nameID',{}).get(language,''),
                            description=bloodlines[bloodlineid].get('descriptionID',{}).get(language,''),
                            iconID=bloodlines[bloodlineid].get('iconID'),
                            corporationID=bloodlines[bloodlineid].get('corporationID'),
                            charisma=bloodlines[bloodlineid].get('charisma'),
                            intelligence=bloodlines[bloodlineid].get('intelligence'),
                            memory=bloodlines[bloodlineid].get('memory'),
                            perception=bloodlines[bloodlineid].get('perception'),
                            raceID=bloodlines[bloodlineid].get('raceID'),
                            shipTypeID=bloodlines[bloodlineid].get('shipTypeID'),
            ))
    trans.commit()
