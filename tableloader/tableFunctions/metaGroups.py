# -*- coding: utf-8 -*-
import sys
import os
reload(sys)
sys.setdefaultencoding("utf-8")
from sqlalchemy import Table

from yaml import load
try:
	from yaml import CSafeLoader as SafeLoader
	print "Using CSafeLoader"
except ImportError:
	from yaml import SafeLoader
	print "Using Python SafeLoader"


def importyaml(connection,metadata,sourcePath,language='en'):
    print "Importing metaGroups"
    invMetaGroups = Table('invMetaGroups',metadata)
    trnTranslations = Table('trnTranslations',metadata)
    
    print "opening Yaml"
        
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','metaGroups.yaml'),'r') as yamlstream:
        print "importing"
        metagroups=load(yamlstream,Loader=SafeLoader)
        print "Yaml Processed into memory"
        for metagroupid in metagroups:
            connection.execute(invMetaGroups.insert(),
                            metaGroupID=metagroupid,
                            metaGroupName=metagroups[metagroupid].get('nameID',{}).get(language,'').decode('utf-8'),
                            iconID=metagroups[metagroupid].get('iconID'),
                            description=metagroups[metagroupid].get('descriptionID',{}).get(language,'').decode('utf-8')
            )
            
            if (metagroups[metagroupid].has_key('nameID')):
                for lang in metagroups[metagroupid]['nameID']:
                    try:
                        connection.execute(trnTranslations.insert(),tcID=34,keyID=metagroupid,languageID=lang,text=metagroups[metagroupid]['nameID'][lang].decode('utf-8'));
                    except:                        
                        print '{} {} has a category problem'.format(categoryid,lang)
            if (metagroups[metagroupid].has_key('descriptionID')):
                for lang in metagroups[metagroupid]['descriptionID']:
                    try:
                        connection.execute(trnTranslations.insert(),tcID=35,keyID=metagroupid,languageID=lang,text=metagroups[metagroupid]['descriptionID'][lang].decode('utf-8'));
                    except:                        
                        print '{} {} has a category problem'.format(categoryid,lang)
    trans.commit()
