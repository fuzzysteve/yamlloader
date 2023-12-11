import sys
import os
from sqlalchemy import Table

from yaml import load
try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")


def importyaml(connection,metadata,sourcePath,language='en'):
    print("Importing marketGroups")
    invMarketGroups = Table('invMarketGroups',metadata)
    trnTranslations = Table('trnTranslations',metadata)
    
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','marketGroups.yaml')) as yamlstream:
        print(f"importing {os.path.basename(yamlstream.name)}")
        marketgroups=load(yamlstream,Loader=SafeLoader)
        print(f"{os.path.basename(yamlstream.name)} loaded")
        for marketgroupid in marketgroups:
            connection.execute(invMarketGroups.insert().values(
                            marketGroupID=marketgroupid,
                            parentGroupID=marketgroups[marketgroupid].get('parentGroupID',None),
                            marketGroupName=marketgroups[marketgroupid].get('nameID',{}).get(language,''),
                            description=marketgroups[marketgroupid].get('descriptionID',{}).get(language,''),
                            iconID=marketgroups[marketgroupid].get('iconID'),
                            hasTypes=marketgroups[marketgroupid].get('hasTypes',False)
            ))
            
            if 'nameID' in marketgroups[marketgroupid]:
                for lang in marketgroups[marketgroupid]['nameID']:
                    try:
                        connection.execute(trnTranslations.insert().values(tcID=36,keyID=marketgroupid,languageID=lang,text=marketgroups[marketgroupid]['nameID'][lang]))
                    except:                        
                        print(f'{marketgroupid} {lang} has a category problem')
            if 'descriptionID' in marketgroups[marketgroupid]:
                for lang in marketgroups[marketgroupid]['descriptionID']:
                    try:
                        connection.execute(trnTranslations.insert().values(tcID=37,keyID=marketgroupid,languageID=lang,text=marketgroups[marketgroupid]['descriptionID'][lang]))
                    except:                        
                        print(f'{marketgroupid} {lang} has a category problem')
    trans.commit()
