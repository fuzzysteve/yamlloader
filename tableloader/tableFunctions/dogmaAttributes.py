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
    with open(os.path.join(sourcePath,'fsd','dogmaAttributes.yaml')) as yamlstream:
        print(f"importing {os.path.basename(yamlstream.name)}")
        dogmaAttributes=load(yamlstream,Loader=SafeLoader)
        print(f"{os.path.basename(yamlstream.name)} loaded")
        for dogmaAttributeID in dogmaAttributes:
          attribute = dogmaAttributes[dogmaAttributeID]
          connection.execute(dgmAttributes.insert().values(
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
                ))
    trans.commit()
