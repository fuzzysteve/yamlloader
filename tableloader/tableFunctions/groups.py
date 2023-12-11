from yaml import load, dump
try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")

import os
import sys
from sqlalchemy import Table

def importyaml(connection,metadata,sourcePath,language='en'):
    invGroups = Table('invGroups',metadata)
    trnTranslations = Table('trnTranslations',metadata)
    print("Importing Groups")
    with open(os.path.join(sourcePath,'fsd','groupIDs.yaml')) as yamlstream:
        print(f"importing {os.path.basename(yamlstream.name)}")
        trans = connection.begin()
        groupids=load(yamlstream,Loader=SafeLoader)
        print(f"{os.path.basename(yamlstream.name)} loaded")
        for groupid in groupids:
            connection.execute(invGroups.insert().values(
                            groupID=groupid,
                            categoryID=groupids[groupid].get('categoryID',0),
                            groupName=groupids[groupid].get('name',{}).get(language,''),
                            iconID=groupids[groupid].get('iconID'),
                            useBasePrice=groupids[groupid].get('useBasePrice'),
                            anchored=groupids[groupid].get('anchored',0),
                            anchorable=groupids[groupid].get('anchorable',0),
                            fittableNonSingleton=groupids[groupid].get('fittableNonSingleton',0),
                            published=groupids[groupid].get('published',0)))
            if 'name' in groupids[groupid]:
                for lang in groupids[groupid]['name']:
                    connection.execute(trnTranslations.insert().values(tcID=7,keyID=groupid,languageID=lang,text=groupids[groupid]['name'][lang]))
    trans.commit()
