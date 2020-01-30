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
    print("Importing Categories")
    invCategories = Table('invCategories',metadata)
    trnTranslations = Table('trnTranslations',metadata)
    
    print("opening Yaml")
        
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','categoryIDs.yaml'),'r') as yamlstream:
        print("importing")
        categoryids=load(yamlstream,Loader=SafeLoader)
        print("Yaml Processed into memory")
        for categoryid in categoryids:
            connection.execute(invCategories.insert(),
                            categoryID=categoryid,
                            categoryName=categoryids[categoryid].get('name',{}).get(language,''),
                            iconID=categoryids[categoryid].get('iconID'),
                            published=categoryids[categoryid].get('published',0))
            
            if ('name' in categoryids[categoryid]):
                for lang in categoryids[categoryid]['name']:
                    try:
                        connection.execute(trnTranslations.insert(),tcID=6,keyID=categoryid,languageID=lang,text=categoryids[categoryid]['name'][lang])
                    except:                        
                        print('{} {} has a category problem'.format(categoryid,lang))
    trans.commit()
