import os
import sys
import typing

import sqlalchemy.exc
from sqlalchemy import Table
from yaml import load

try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")


def importyaml(connection,metadata,sourcePath,language='en'):
    print("Importing Categories")
    invCategories = Table('invCategories',metadata, autoload_with=connection)
    trnTranslations = Table('trnTranslations',metadata, autoload_with=connection)
    
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','categoryIDs.yaml')) as yamlstream:
        print(f"importing {os.path.basename(yamlstream.name)}")
        categoryids: dict[int, dict] = load(yamlstream,Loader=SafeLoader)
        print(f"{os.path.basename(yamlstream.name)} loaded")
        for categoryid, categorydata in categoryids.items():
            connection.execute(invCategories.insert().values(
                            categoryID=categoryid,
                            categoryName=categorydata.get('name',{}).get(language,''),
                            iconID=categorydata.get('iconID', 0),
                            published=categorydata.get('published',0)))
            
            if 'name' in categorydata.keys():
                for lang in categorydata['name']:
                    try:
                        connection.execute(trnTranslations.insert().values(tcID=6,keyID=categoryid,languageID=lang,text=categoryids[categoryid]['name'][lang]))
                    except:                        
                        print(f'{categoryid} {lang} has a category problem')
    trans.commit()
