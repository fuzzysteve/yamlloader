# -*- coding: utf-8 -*-
import os
import yaml
from sqlalchemy import Table

def importyaml(connection,metadata,sourcePath):
    invGroups = Table('invGroups',metadata)
    trnTranslations = Table('trnTranslations',metadata)
    print("Importing Groups")
    print("opening Yaml")
    with open(os.path.join(sourcePath,'fsd','groupIDs.yaml'),'r') as yamlstream:
        trans = connection.begin()
        groupids=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
        print("Yaml Processed into memory")
        for groupid in groupids:
            connection.execute(invGroups.insert(),
                            groupID=groupid,
                            categoryID=groupids[groupid].get('categoryID',0),
                            groupName=groupids[groupid].get('name',{}).get('en',''),
                            iconID=groupids[groupid].get('iconID'),
                            useBasePrice=groupids[groupid].get('useBasePrice'),
                            anchored=groupids[groupid].get('anchored',0),
                            anchorable=groupids[groupid].get('anchorable',0),
                            fittableNonSingleton=groupids[groupid].get('fittableNonSingleton',0),
                            published=groupids[groupid].get('published',0))
            if 'name' in groupids[groupid]:
                for lang in groupids[groupid]['name']:
                    connection.execute(trnTranslations.insert(),tcID=7,keyID=groupid,languageID=lang,text=groupids[groupid]['name'][lang]);
    trans.commit()
