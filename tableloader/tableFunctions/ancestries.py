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
    print("Importing character Ancestries")
    chrAncestries = Table('chrAncestries',metadata)
    
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','ancestries.yaml')) as yamlstream:
        print(f"importing {os.path.basename(yamlstream.name)}")
        characterancestries=load(yamlstream,Loader=SafeLoader)
        print(f"{os.path.basename(yamlstream.name)} loaded")
        for ancestryid in characterancestries:
            connection.execute(chrAncestries.insert().values(
                            ancestryID=ancestryid,
                            ancestryName=characterancestries[ancestryid].get('nameID',{}).get(language,''),
                            description=characterancestries[ancestryid].get('descriptionID',{}).get(language,''),
                            iconID=characterancestries[ancestryid].get('iconID'),
                            bloodlineID=characterancestries[ancestryid].get('bloodlineID'),
                            charisma=characterancestries[ancestryid].get('charisma'),
                            intelligence=characterancestries[ancestryid].get('intelligence'),
                            memory=characterancestries[ancestryid].get('memory'),
                            perception=characterancestries[ancestryid].get('perception'),
                            shortDescription=characterancestries[ancestryid].get('shortDescription')
            ))
    trans.commit()
