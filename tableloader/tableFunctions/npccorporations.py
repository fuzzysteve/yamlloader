# -*- coding: utf-8 -*-
import sys
import os
#sys.setdefaultencoding("utf-8")
from sqlalchemy import Table

from yaml import load
try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")


def importyaml(connection,metadata,sourcePath,language='en'):
    print("Importing NPC corporations")
    crpNPCCorporations = Table('crpNPCCorporations',metadata)
    invNames =  Table('invNames', metadata) 
        
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','npcCorporations.yaml'),'r') as yamlstream:
        print("importing {}".format(os.path.basename(yamlstream.name)))
        npccorps=load(yamlstream,Loader=SafeLoader)
        print("{} loaded".format(os.path.basename(yamlstream.name)))
        for corpid in npccorps:
            connection.execute(crpNPCCorporations.insert(),
                            corporationID=corpid,
                            description=npccorps[corpid].get('descriptionID',{}).get(language,''),
                            iconID=npccorps[corpid].get('iconID'),
                            enemyID=npccorps[corpid].get('enemyID'),
                            factionID=npccorps[corpid].get('factionID'),
                            friendID=npccorps[corpid].get('friendID'),
                            initialPrice=npccorps[corpid].get('initialPrice'),
                            minSecurity=npccorps[corpid].get('minSecurity'),
                            publicShares=npccorps[corpid].get('publicShares'),
                            size=npccorps[corpid].get('size'),
                            solarSystemID=npccorps[corpid].get('solarSystemID'),
                            extent=npccorps[corpid].get('extent'),
                              ) 
#            connection.execute(invNames.insert(),
#                           itemID=corpid,
#                           itemName=npccorps[corpid].get('nameID',{}).get(language,'')
#                          )
    trans.commit()
