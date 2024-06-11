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
    print "Importing Categories"
    invCategories = Table('invCategories',metadata)
    trnTranslations = Table('trnTranslations',metadata)
    
    print "opening Yaml"
        
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','categories.yaml'),'r') as yamlstream:
        print "importing"
        categoryids=load(yamlstream,Loader=SafeLoader)
        print "Yaml Processed into memory"
        for categoryid in categoryids:
            connection.execute(invCategories.insert(),
                            categoryID=categoryid,
                            categoryName=categoryids[categoryid].get('name',{}).get(language,'').decode('utf-8'),
                            iconID=categoryids[categoryid].get('iconID'),
                            published=categoryids[categoryid].get('published',0))
            
            if (categoryids[categoryid].has_key('name')):
                for lang in categoryids[categoryid]['name']:
                    try:
                        connection.execute(trnTranslations.insert(),tcID=6,keyID=categoryid,languageID=lang,text=categoryids[categoryid]['name'][lang].decode('utf-8'));
                    except:                        
                        print '{} {} has a category problem'.format(categoryid,lang)
    trans.commit()
