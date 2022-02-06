# -*- coding: utf-8 -*-
import sys
import os
from sqlalchemy import Table

from yaml import load,dump
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader
    print("Using Python SafeLoader")



def importyaml(connection,metadata,sourcePath,language='en'):
    print("Importing dogma attribute categories")
    dgmAttributeCategories = Table('dgmAttributeCategories',metadata)
    
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','dogmaAttributeCategories.yaml'),'r') as yamlstream:
        print("importing {}".format(os.path.basename(yamlstream.name)))
        dogmaAttributeCategories=load(yamlstream,Loader=SafeLoader)
        print("{} loaded".format(os.path.basename(yamlstream.name)))
        for dogmaAttributeCategoryID in dogmaAttributeCategories:
            attribute = dogmaAttributeCategories[dogmaAttributeCategoryID]
            connection.execute(dgmAttributeCategories.insert(),
                categoryID=dogmaAttributeCategoryID,
                categoryName=attribute['name'],
                categoryDescription=attribute.get('description', attribute['name'])
            )
    trans.commit()

