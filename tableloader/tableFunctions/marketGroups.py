# -*- coding: utf-8 -*-
import sys
import os
import importlib
importlib.reload(sys)
from sqlalchemy import Table

from yaml import load
try:
	from yaml import CSafeLoader as SafeLoader
	print("Using CSafeLoader")
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")


def importyaml(connection,metadata,sourcePath,language='en'):
    print("Importing marketGroups")
    invMarketGroups = Table('invMarketGroups',metadata)
    trnTranslations = Table('trnTranslations',metadata)
    
    print("opening Yaml")
        
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','marketGroups.yaml'),'r') as yamlstream:
        print("importing")
        marketgroups=load(yamlstream,Loader=SafeLoader)
        print("Yaml Processed into memory")
        for marketgroupid in marketgroups:
            connection.execute(invMarketGroups.insert(),
                            marketGroupID=marketgroupid,
                            parentGroupID=marketgroups[marketgroupid].get('parentGroupID',None),
                            marketGroupName=marketgroups[marketgroupid].get('nameID',{}).get(language,''),
                            description=marketgroups[marketgroupid].get('descriptionID',{}).get(language,''),
                            iconID=marketgroups[marketgroupid].get('iconID'),
                            hasTypes=marketgroups[marketgroupid].get('hasTypes',False)
            )
            
            if ('nameID' in marketgroups[marketgroupid]):
                for lang in marketgroups[marketgroupid]['nameID']:
                    try:
                        connection.execute(trnTranslations.insert(),tcID=36,keyID=marketgroupid,languageID=lang,text=marketgroups[marketgroupid]['nameID'][lang])
                    except:                        
                        print('{} {} has a category problem'.format(categoryid,lang))
            if ('descriptionID' in marketgroups[marketgroupid]):
                for lang in marketgroups[marketgroupid]['descriptionID']:
                    try:
                        connection.execute(trnTranslations.insert(),tcID=37,keyID=marketgroupid,languageID=lang,text=marketgroups[marketgroupid]['descriptionID'][lang])
                    except:                        
                        print('{} {} has a category problem'.format(categoryid,lang))
    trans.commit()
