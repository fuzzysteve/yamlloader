# -*- coding: utf-8 -*-
from yaml import load, dump
try:
	from yaml import CSafeLoader as SafeLoader
	print "Using CSafeLoader"
except ImportError:
	from yaml import SafeLoader
	print "Using Python SafeLoader"

import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from sqlalchemy import Table

def importyaml(connection,metadata,sourcePath,language='en'):
    invGroups = Table('invGroups',metadata)
    trnTranslations = Table('trnTranslations',metadata)
    print "Importing Groups"
    print "opening Yaml"
    with open(os.path.join(sourcePath,'fsd','groups.yaml'),'r') as yamlstream:
        trans = connection.begin()
        groupids=load(yamlstream,Loader=SafeLoader)
        print "Yaml Processed into memory"
        for groupid in groupids:
            connection.execute(invGroups.insert(),
                            groupID=groupid,
                            categoryID=groupids[groupid].get('categoryID',0),
                            groupName=groupids[groupid].get('name',{}).get(language,'').decode('utf-8'),
                            iconID=groupids[groupid].get('iconID'),
                            useBasePrice=groupids[groupid].get('useBasePrice'),
                            anchored=groupids[groupid].get('anchored',0),
                            anchorable=groupids[groupid].get('anchorable',0),
                            fittableNonSingleton=groupids[groupid].get('fittableNonSingleton',0),
                            published=groupids[groupid].get('published',0))
            if (groupids[groupid].has_key('name')):
                for lang in groupids[groupid]['name']:
                    connection.execute(trnTranslations.insert(),tcID=7,keyID=groupid,languageID=lang,text=groupids[groupid]['name'][lang].decode('utf-8'));
    trans.commit()
