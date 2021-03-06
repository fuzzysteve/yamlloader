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
    print "Importing character factions"
    chrFactions = Table('chrFactions',metadata)
    
    print "opening Yaml"
        
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','factions.yaml'),'r') as yamlstream:
        print "importing"
        characterfactions=load(yamlstream,Loader=SafeLoader)
        print "Yaml Processed into memory"
        for factionid in characterfactions:
            connection.execute(chrFactions.insert(),
                            factionID=factionid,
                            factionName=characterfactions[factionid].get('nameID',{}).get(language,'').decode('utf-8'),
                            description=characterfactions[factionid].get('descriptionID',{}).get(language,'').decode('utf-8'),
                            iconID=characterfactions[factionid].get('iconID'),
                            raceIDs=characterfactions[factionid].get('memberRaces',[0])[0],
                            solarSystemID=characterfactions[factionid].get('solarSystemID'),
                            corporationID=characterfactions[factionid].get('corporationID'),
                            sizeFactor=characterfactions[factionid].get('sizeFactor'),
                            militiaCorporationID=characterfactions[factionid].get('militiaCorporationID'),
                              ) 
    trans.commit()
