# -*- coding: utf-8 -*-
import os

from utils import yaml_stream

from sqlalchemy import Table

def load(connection, metadata, sourcePath, language='en'):

    invGroups       = Table('invGroups',metadata)
    trnTranslations = Table('trnTranslations',metadata)

    print("Importing Groups")

    trans = connection.begin()

    with open(os.path.join(sourcePath,'fsd','groupIDs.yaml'),'r') as yamlstream:
        for group in yaml_stream.read_by_any(yamlstream):
            for group_id, group_details in group.items():
                connection.execute(invGroups.insert(),
                                groupID=group_id,
                                categoryID=group_details.get('categoryID',0),
                                groupName=group_details.get('name',{}).get(language,''),
                                iconID=group_details.get('iconID'),
                                useBasePrice=group_details.get('useBasePrice'),
                                anchored=group_details.get('anchored',0),
                                anchorable=group_details.get('anchorable',0),
                                fittableNonSingleton=group_details.get('fittableNonSingleton',0),
                                published=group_details.get('published',0))
                if 'name' in group_details:
                    for lang in group_details['name']:
                        connection.execute(trnTranslations.insert(),tcID=7,keyID=group_id,languageID=lang,text=group_details['name'][lang]);
    trans.commit()
