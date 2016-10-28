# -*- coding: utf-8 -*-
import yaml
import os
from sqlalchemy import Table;


def importyaml(connection,metadata,sourcePath):

    activityIDs={"copying":5,"manufacturing":1,"research_material":4,"research_time":3,"invention":8};

    industryBlueprints=Table('industryBlueprints',metadata)
    industryActivity = Table('industryActivity',metadata)
    industryActivityMaterials = Table('industryActivityMaterials',metadata)
    industryActivityProducts = Table('industryActivityProducts',metadata)
    industryActivitySkills = Table('industryActivitySkills',metadata)
    industryActivityProbabilities = Table('industryActivityProbabilities',metadata)
    
    
    

    print("importing Blueprints")
    print("opening Yaml")
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','blueprints.yaml'),'r') as yamlstream:
        blueprints=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
        print("Yaml Processed into memory")
        for blueprint in blueprints:
            connection.execute(industryBlueprints.insert(),typeID=blueprint,maxProductionLimit=blueprints[blueprint]["maxProductionLimit"])
            for activity in blueprints[blueprint]['activities']:
                connection.execute(industryActivity.insert(),
                                    typeID=blueprint,
                                    activityID=activityIDs[activity],
                                    time=blueprints[blueprint]['activities'][activity]['time'])
                if 'materials' in blueprints[blueprint]['activities'][activity]:
                    for material in blueprints[blueprint]['activities'][activity]['materials']:
                        connection.execute(industryActivityMaterials.insert(),
                                            typeID=blueprint,
                                            activityID=activityIDs[activity],
                                            materialTypeID=material['typeID'],
                                            quantity=material['quantity'])
                if 'products' in blueprints[blueprint]['activities'][activity]:
                    for product in blueprints[blueprint]['activities'][activity]['products']:
                        connection.execute(industryActivityProducts.insert(),
                                            typeID=blueprint,
                                            activityID=activityIDs[activity],
                                            productTypeID=product['typeID'],
                                            quantity=product['quantity'])
                        if 'probability' in product:
                            connection.execute(industryActivityProbabilities.insert(),
                                                typeID=blueprint,
                                                activityID=activityIDs[activity],
                                                productTypeID=product['typeID'],
                                                probability=product['probability'])
                try:
                    if 'skills' in blueprints[blueprint]['activities'][activity]:
                        for skill in blueprints[blueprint]['activities'][activity]['skills']:
                            connection.execute(industryActivitySkills.insert(),
                                                typeID=blueprint,
                                                activityID=activityIDs[activity],
                                                skillID=skill['typeID'],
                                                level=skill['level'])
                except:
                    print('{} has a bad skill'.format(blueprint))
    trans.commit()
