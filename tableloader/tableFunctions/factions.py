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
    print("Importing character factions")
    chrFactions = Table('chrFactions',metadata)
    
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','factions.yaml')) as yamlstream:
        print(f"importing {os.path.basename(yamlstream.name)}")
        characterfactions=load(yamlstream,Loader=SafeLoader)
        print(f"{os.path.basename(yamlstream.name)} loaded")
        for factionid in characterfactions:
            connection.execute(chrFactions.insert().values(
                            factionID=factionid,
                            factionName=characterfactions[factionid].get('nameID',{}).get(language,'en'),
                            description=characterfactions[factionid].get('descriptionID',{}).get(language,'en'),
                            iconID=characterfactions[factionid].get('iconID'),
                            raceIDs=characterfactions[factionid].get('memberRaces',[0])[0],
                            solarSystemID=characterfactions[factionid].get('solarSystemID'),
                            corporationID=characterfactions[factionid].get('corporationID'),
                            sizeFactor=characterfactions[factionid].get('sizeFactor'),
                            militiaCorporationID=characterfactions[factionid].get('militiaCorporationID'),
            ))
    trans.commit()
