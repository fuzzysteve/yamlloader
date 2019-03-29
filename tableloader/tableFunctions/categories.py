# -*- coding: utf-8 -*-
import os

from utils import yaml_stream

from sqlalchemy import Table

def load(connection, metadata, sourcePath, language='en'):

    print("Importing Categories")

    invCategories = Table('invCategories',metadata)
    trnTranslations = Table('trnTranslations',metadata)

    print("opening Yaml")

    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','categoryIDs.yaml'),'r') as yamlstream:
        for category in yaml_stream.read_by_any(yamlstream):
            for category_id, category_details in category.items():
                connection.execute(invCategories.insert(),
                                categoryID=category_id,
                                categoryName=category_details.get('name',{}).get(language,''),
                                iconID=category_details.get('iconID'),
                                published=category_details.get('published',0))

                if 'name' in category_details:
                    for lang in category_details['name']:
                        try:
                            connection.execute(trnTranslations.insert(),tcID=6,keyID=category_id,languageID=lang,text=category_details['name'][lang]);
                        except:                        
                            print('{} {} has a category problem'.format(category_id,lang))
    trans.commit()
