# -*- coding: utf-8 -*-
import sys
import os
reload(sys)
sys.setdefaultencoding("utf-8")
from sqlalchemy import Table

from yaml import load,dump
try:
	from yaml import CSafeLoader as SafeLoader
	print "Using CSafeLoader"
except ImportError:
	from yaml import SafeLoader
	print "Using Python SafeLoader"



def importyaml(connection,metadata,sourcePath,language='en'):
    print "Importing dogma attributes"
    dgmAttributes = Table('dgmAttributeTypess',metadata)
    
    print "opening Yaml"
        
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','dogmaAttributes.yaml'),'r') as yamlstream:
        print "importing"
        dogmaAttributeCategories=load(yamlstream,Loader=SafeLoader)
        print "Yaml Processed into memory"
        for dogmaAttributeID in dogmaAttributes:
          attribute = dogmaAttributes[dogmaAttributeID]
          connection.execute(dgmAttributes.insert(),
                               attributeID=dogmaAttributeID,
                               categoryID=attribute['categoryID'],
                               defaultValue=attribute.get('defaultValue'),
                               description=attribute.get('description'),
                               iconID=attribute.get('iconID'),
                               attributeName=attribute.get('displayNameID',[]).get(language),
                               published=attribute.get('published'),
                               unitID=attribute.get('unitID'),
                               stackable=attribute.get('stackable'),
                               highIsGood=attribute.get('highIsGood'),
                               displayName=attribute.get('displayNameID',[]).get(language)
                )
    trans.commit()
