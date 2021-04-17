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
    print("Importing dogma attributes")
    dgmAttributes = Table('dgmAttributeTypes',metadata)
    
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','dogmaAttributes.yaml'),'r') as yamlstream:
        print("importing {}".format(os.path.basename(yamlstream.name)))
        dogmaAttributes=load(yamlstream,Loader=SafeLoader)
        print("{} loaded".format(os.path.basename(yamlstream.name)))
        for dogmaAttributeID in dogmaAttributes:
          attribute = dogmaAttributes[dogmaAttributeID]
          connection.execute(dgmAttributes.insert(),
                               attributeID=dogmaAttributeID,
                               categoryID=attribute.get('categoryID'),
                               defaultValue=attribute.get('defaultValue'),
                               description=attribute.get('description'),
                               iconID=attribute.get('iconID'),
                               attributeName=attribute.get('displayNameID',{}).get(language),
                               published=attribute.get('published'),
                               unitID=attribute.get('unitID'),
                               stackable=attribute.get('stackable'),
                               highIsGood=attribute.get('highIsGood'),
                               displayName=attribute.get('displayNameID',{}).get(language)
                )
    trans.commit()
