from yaml import load
try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")

import os
import typing
import sqlalchemy
from sqlalchemy import Table

def importyaml(connection,metadata,sourcePath):

    activityIDs={"copying":5,"manufacturing":1,"research_material":4,"research_time":3,"invention":8,"reaction":11}

    industryBlueprints=Table('industryBlueprints',metadata)
    industryActivity = Table('industryActivity',metadata)
    industryActivityMaterials = Table('industryActivityMaterials',metadata)
    industryActivityProducts = Table('industryActivityProducts',metadata)
    industryActivitySkills = Table('industryActivitySkills',metadata)
    industryActivityProbabilities = Table('industryActivityProbabilities',metadata)
    

    print("importing Blueprints")
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','blueprints.yaml')) as yamlstream:
        print(f"importing {os.path.basename(yamlstream.name)}")
        blueprints: dict[int, dict] = load(yamlstream,Loader=SafeLoader)
        print(f"{os.path.basename(yamlstream.name)} loaded")
        industryActivitySkills_seen: typing.Final = set()
        for blueprint in blueprints.keys():
            connection.execute(industryBlueprints.insert().values(typeID=blueprint,maxProductionLimit=blueprints[blueprint]["maxProductionLimit"]))
            for activity in blueprints[blueprint]['activities'].keys():
                connection.execute(industryActivity.insert().values(
                                    typeID=blueprint,
                                    activityID=activityIDs[activity],
                                    time=blueprints[blueprint]['activities'][activity]['time']))
                if 'materials' in blueprints[blueprint]['activities'][activity]:
                    for material in blueprints[blueprint]['activities'][activity]['materials']:
                        connection.execute(industryActivityMaterials.insert().values(
                                            typeID=blueprint,
                                            activityID=activityIDs[activity],
                                            materialTypeID=material['typeID'],
                                            quantity=material['quantity']))
                if 'products' in blueprints[blueprint]['activities'][activity]:
                    for product in blueprints[blueprint]['activities'][activity]['products']:
                        connection.execute(industryActivityProducts.insert().values(
                                            typeID=blueprint,
                                            activityID=activityIDs[activity],
                                            productTypeID=product['typeID'],
                                            quantity=product['quantity']))
                        if 'probability' in product:
                            connection.execute(industryActivityProbabilities.insert().values(
                                                typeID=blueprint,
                                                activityID=activityIDs[activity],
                                                productTypeID=product['typeID'],
                                                probability=product['probability']))
                try:
                    if 'skills' in blueprints[blueprint]['activities'][activity]:
                        for skill in blueprints[blueprint]['activities'][activity]['skills']:
                            blueprint_activity_type_key: typing.Final = f"{blueprint}-{activityIDs[activity]}-{skill['typeID']}-{skill['level']}"
                            if not blueprint_activity_type_key in industryActivitySkills_seen:
                                industryActivitySkills_seen.add(blueprint_activity_type_key)
                                connection.execute(industryActivitySkills.insert().values(
                                                    typeID=blueprint,
                                                    activityID=activityIDs[activity],
                                                    skillID=skill['typeID'],
                                                    level=skill['level']))
                except:
                    print(f'{blueprint} ({blueprints[blueprint]}) has a bad skill')
    trans.commit()
