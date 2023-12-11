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
    print("Importing metaGroups")
    invMetaGroups = Table('invMetaGroups',metadata)
    trnTranslations = Table('trnTranslations',metadata)
    
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','metaGroups.yaml')) as yamlstream:
        print(f"importing {os.path.basename(yamlstream.name)}")
        metagroups=load(yamlstream,Loader=SafeLoader)
        print(f"{os.path.basename(yamlstream.name)} loaded")
        for metagroupid in metagroups:
            connection.execute(invMetaGroups.insert().values(
                            metaGroupID=metagroupid,
                            metaGroupName=metagroups[metagroupid].get('nameID',{}).get(language,''),
                            iconID=metagroups[metagroupid].get('iconID'),
                            description=metagroups[metagroupid].get('descriptionID',{}).get(language,'')
            ))
            
            if 'nameID' in metagroups[metagroupid]:
                for lang in metagroups[metagroupid]['nameID']:
                    try:
                        connection.execute(trnTranslations.insert().values(tcID=34,keyID=metagroupid,languageID=lang,text=metagroups[metagroupid]['nameID'][lang]))
                    except:                        
                        print(f'{metagroupid} {lang} has a category problem')
            if 'descriptionID' in metagroups[metagroupid]:
                for lang in metagroups[metagroupid]['descriptionID']:
                    try:
                        connection.execute(trnTranslations.insert().values(tcID=35,keyID=metagroupid,languageID=lang,text=metagroups[metagroupid]['descriptionID'][lang]))
                    except:                        
                        print(f'{metagroupid} {lang} has a category problem')
    trans.commit()
