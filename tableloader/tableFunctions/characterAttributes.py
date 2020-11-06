# -*- coding: utf-8 -*-
import sys
import os
reload(sys)
sys.setdefaultencoding("utf-8")
from sqlalchemy import Table

from yaml import load
try:
	from yaml import CSafeLoader as SafeLoader
	print "Using CSafeLoader"
except ImportError:
	from yaml import SafeLoader
	print "Using Python SafeLoader"


def importyaml(connection,metadata,sourcePath,language='en'):
    print "Importing character Attributes"
    chrAttributes = Table('chrAttributes',metadata)
    
    print "opening Yaml"
        
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','characterAttributes.yaml'),'r') as yamlstream:
        print "importing"
        characterattributes=load(yamlstream,Loader=SafeLoader)
        print "Yaml Processed into memory"
        for attributeid in characterattributes:
            connection.execute(chrAttributes.insert(),
                            attributeID=attributeid,
                            attributeName=characterattributes[attributeid].get('nameID',{}).get(language,'').decode('utf-8'),
                            description=characterattributes[attributeid].get('description',''),
                            iconID=characterattributes[attributeid].get('iconID',None),
                            notes=characterattributes[attributeid].get('notes',''),
                            shortDescription=characterattributes[attributeid].get('shortDescription',''),
                              ) 
    trans.commit()
