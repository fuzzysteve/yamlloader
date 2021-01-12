# -*- coding: utf-8 -*-
from yaml import load, dump
try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")

import os
import sys
#sys.setdefaultencoding("utf-8")
from sqlalchemy import Table

def importyaml(connection,metadata,sourcePath,language='en'):
    agtAgents = Table('agtAgents',metadata)
    agtAgentsInSpace = Table('agtAgentsInSpace',metadata)
    agtResearchAgents = Table ('agtResearchAgents',metadata)
    print("Importing Agents")
    with open(os.path.join(sourcePath,'fsd','agents.yaml'),'r') as yamlstream:
        print("importing {}".format(os.path.basename(yamlstream.name)))
        trans = connection.begin()
        agents=load(yamlstream,Loader=SafeLoader)
        print("{} loaded".format(os.path.basename(yamlstream.name)))
        for agentid in agents:
            connection.execute(agtAgents.insert(),
                            agentID=agentid,
                            divisionID=agents[agentid].get('divisionID',None),
                            corporationID=agents[agentid].get('corporationID',None),
                            isLocator=agents[agentid].get('isLocator',None),
                            level=agents[agentid].get('level',None),
                            locationID=agents[agentid].get('locationID',None),
                            agentTypeID=agents[agentid].get('agentTypeID',None),
                              )
    trans.commit()
    print("Importing AgentsInSpace")
    with open(os.path.join(sourcePath,'fsd','agentsInSpace.yaml'),'r') as yamlstream:
        print("importing {}".format(os.path.basename(yamlstream.name)))
        trans = connection.begin()
        agents=load(yamlstream,Loader=SafeLoader)
        print("{} loaded".format(os.path.basename(yamlstream.name)))
        for agentid in agents:
            connection.execute(agtAgentsInSpace.insert(),
                            agentID=agentid,
                            dungeonID=agents[agentid].get('dungeonID',None),
                            solarSystemID=agents[agentid].get('solarSystemID',None),
                            spawnPointID=agents[agentid].get('spawnPointID',None),
                            typeID=agents[agentid].get('typeID',None),
                              )
    trans.commit()
    print("Importing research agents")
    with open(os.path.join(sourcePath,'fsd','researchAgents.yaml'),'r') as yamlstream:
        print("importing {}".format(os.path.basename(yamlstream.name)))
        trans = connection.begin()
        agents=load(yamlstream,Loader=SafeLoader)
        print("{} loaded".format(os.path.basename(yamlstream.name)))
        for agentid in agents:
            for skill in agents[agentid]['skills']:
                connection.execute(agtResearchAgents.insert(),
                                agentID=agentid,
                                typeID=skill.get('typeID',None),
                              )
    trans.commit()
