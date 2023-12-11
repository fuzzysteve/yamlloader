import sys
import os
from sqlalchemy import Table

from yaml import load,dump
try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")


distribution={'twosome':1,'bubble':2}
effectcategory={}


def importyaml(connection,metadata,sourcePath,language='en'):
    print("Importing dogma effects")
    dgmEffects = Table('dgmTypeEffects',metadata)
    dgmAttributes = Table('dgmTypeAttributes',metadata)
    
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','typeDogma.yaml')) as yamlstream:
        print(f"importing {os.path.basename(yamlstream.name)}")
        dogmaEffects=load(yamlstream,Loader=SafeLoader)
        print(f"{os.path.basename(yamlstream.name)} loaded")
        for typeid in dogmaEffects:
            for effect in dogmaEffects[typeid]['dogmaEffects']:
                connection.execute(dgmEffects.insert().values(
                                typeID=typeid,
                                effectID=effect['effectID'],
                                isDefault=effect.get('isDefault')
                ))
            for attribute in dogmaEffects[typeid]['dogmaAttributes']:
                connection.execute(dgmAttributes.insert().values(
                                typeID=typeid,
                                attributeID=attribute.get('attributeID'),
                                valueFloat=attribute.get('value')
                ))
    trans.commit()
