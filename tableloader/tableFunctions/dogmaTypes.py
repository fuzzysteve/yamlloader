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


distribution={'twosome':1,'bubble':2}
effectcategory={}


def importyaml(connection,metadata,sourcePath,language='en'):
    print "Importing dogma effects"
    dgmEffects = Table('dgmTypeEffects',metadata)
    dgmAttributes = Table('dgmTypeAttributes',metadata)
    
    print "opening Yaml"
        
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','typeDogma.yaml'),'r') as yamlstream:
        print "importing"
        dogmaEffects=load(yamlstream,Loader=SafeLoader)
        print "Yaml Processed into memory"
        for typeid in dogmaEffects:
            for effect in dogmaEffects[typeid]['dogmaEffects']:
                connection.execute(dgmEffects.insert(),
                                typeID=typeid,
                                effectID=effect.effectID,
                                isDefault=effect.get('isDefault')
                )
            for attribute in dogmaEffects[typeid]['dogmaAttributes']:
                connection.execute(dgmAttributes.insert(),
                                typeID=typeid,
                                attributeID=attribute.attributeID,
                                valueFloat=attribute.value
                )
    trans.commit()
