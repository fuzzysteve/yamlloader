# -*- coding: utf-8 -*-
import os
import yaml
from sqlalchemy import Table

def importyaml(connection,metadata,sourcePath):
    print "Importing Categories"
    invCategories = Table('invCategories',metadata)
    trnTranslations = Table('trnTranslations',metadata)
    
    print "opening Yaml"
        
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','categoryIDs.yaml'),'r') as yamlstream:
        print "importing"
        categoryids=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
        print "Yaml Processed into memory"
        for categoryid in categoryids:
            connection.execute(invCategories.insert(),
                            categoryID=categoryid,
                            categoryName=categoryids[categoryid].get('name',{}).get('en',''),
                            iconID=categoryids[categoryid].get('iconID'),
                            published=categoryids[categoryid].get('published',0))
            
            if (categoryids[categoryid].has_key('name')):
                for lang in categoryids[categoryid]['name']:
                    try:
                        category_text = categoryids[categoryid]['name'][lang]
                        connection.execute(trnTranslations.insert(),tcID=6,keyID=categoryid,languageID=lang,text=category_text);
                    except:                        
                        print '{} {} has a category problem: {}'.format(categoryid, lang, category_text)
    trans.commit()
