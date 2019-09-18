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
    print "Importing marketGroups"
    invMarketGroups = Table('invMarketGroups',metadata)
    trnTranslations = Table('trnTranslations',metadata)
    
    print "opening Yaml"
        
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','marketGroups.yaml'),'r') as yamlstream:
        print "importing"
        marketgroups=load(yamlstream,Loader=SafeLoader)
        print "Yaml Processed into memory"
        for marketgroupid in marketgroups:
            connection.execute(invMarketGroups.insert(),
                            marketGroupID=marketgroupid,
                            parentGroupID=marketgroups[marketgroupid].get('parentGroupID',None),
                            marketGroupName=marketgroups[marketgroupid].get('nameID',{}).get(language,'').decode('utf-8'),
                            description=marketgroups[marketgroupid].get('descriptionID',{}).get(language,'').decode('utf-8'),
                            iconID=marketgroups[marketgroupid].get('iconID'),
                            hasTypes=marketgroups[marketgroupid].get('hasTypes',False)
            )
            
            if (marketgroups[marketgroupid].has_key('nameID')):
                for lang in marketgroups[marketgroupid]['nameID']:
                    try:
                        connection.execute(trnTranslations.insert(),tcID=36,keyID=marketgroupid,languageID=lang,text=marketgroups[marketgroupid]['nameID'][lang].decode('utf-8'));
                    except:                        
                        print '{} {} has a category problem'.format(categoryid,lang)
            if (marketgroups[marketgroupid].has_key('descriptionID')):
                for lang in marketgroups[marketgroupid]['descriptionID']:
                    try:
                        connection.execute(trnTranslations.insert(),tcID=37,keyID=marketgroupid,languageID=lang,text=marketgroups[marketgroupid]['descriptionID'][lang].decode('utf-8'));
                    except:                        
                        print '{} {} has a category problem'.format(categoryid,lang)
    trans.commit()
