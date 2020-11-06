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
    print "Importing character bloodlines"
    chrBloodlines = Table('chrBloodlines',metadata)
    
    print "opening Yaml"
        
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','bloodlines.yaml'),'r') as yamlstream:
        print "importing"
        bloodlines=load(yamlstream,Loader=SafeLoader)
        print "Yaml Processed into memory"
        for bloodlineid in bloodlines:
            connection.execute(chrBloodlines.insert(),
                            bloodlineID=bloodlineid,
                            bloodlineName=bloodlines[bloodlineid].get('nameID',{}).get(language,'').decode('utf-8'),
                            description=bloodlines[bloodlineid].get('descriptionID',{}).get(language,'').decode('utf-8'),
                            iconID=bloodlines[bloodlineid].get('iconID'),
                            corporationID=bloodlines[bloodlineid].get('corporationID'),
                            charisma=bloodlines[bloodlineid].get('charisma'),
                            intelligence=bloodlines[bloodlineid].get('intelligence'),
                            memory=bloodlines[bloodlineid].get('memory'),
                            perception=bloodlines[bloodlineid].get('perception'),
                            raceID=bloodlines[bloodlineid].get('raceID'),
                            shipTypeID=bloodlines[bloodlineid].get('shipTypeID'),
                              ) 
    trans.commit()
