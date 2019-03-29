# -*- coding: utf-8 -*-
import os

from utils import yaml_stream

from sqlalchemy import Table

def load(connection, metadata, sourcePath):

    activityIDs={"copying":5,"manufacturing":1,"research_material":4,"research_time":3,"invention":8,"reaction":11};

    industryBlueprints            = Table('industryBlueprints', metadata)
    industryActivity              = Table('industryActivity', metadata)
    industryActivityMaterials     = Table('industryActivityMaterials', metadata)
    industryActivityProducts      = Table('industryActivityProducts', metadata)
    industryActivitySkills        = Table('industryActivitySkills', metadata)
    industryActivityProbabilities = Table('industryActivityProbabilities', metadata)

    print("Importing Blueprints")
    trans = connection.begin()

    with open(os.path.join(sourcePath,'fsd','blueprints.yaml'),'r') as yamlstream:
        for blueprint in yaml_stream.read_by_any(yamlstream):
            for blueprint_id, blueprint_details in blueprint.items():

                connection.execute(industryBlueprints.insert(),typeID=blueprint_id,maxProductionLimit=blueprint_details["maxProductionLimit"])

                for activity in blueprint_details['activities']:
                    connection.execute(industryActivity.insert(),
                                        typeID=blueprint_id,
                                        activityID=activityIDs[activity],
                                        time=blueprint_details['activities'][activity]['time'])
                    if 'materials' in blueprint_details['activities'][activity]:
                        for material in blueprint_details['activities'][activity]['materials']:
                            connection.execute(industryActivityMaterials.insert(),
                                                typeID=blueprint_id,
                                                activityID=activityIDs[activity],
                                                materialTypeID=material['typeID'],
                                                quantity=material['quantity'])
                    if 'products' in blueprint_details['activities'][activity]:
                        for product in blueprint_details['activities'][activity]['products']:
                            connection.execute(industryActivityProducts.insert(),
                                                typeID=blueprint_id,
                                                activityID=activityIDs[activity],
                                                productTypeID=product['typeID'],
                                                quantity=product['quantity'])
                            if 'probability' in product:
                                connection.execute(industryActivityProbabilities.insert(),
                                                    typeID=blueprint_id,
                                                    activityID=activityIDs[activity],
                                                    productTypeID=product['typeID'],
                                                    probability=product['probability'])
                    try:
                        if 'skills' in blueprint_details['activities'][activity]:
                            for skill in blueprint_details['activities'][activity]['skills']:
                                connection.execute(industryActivitySkills.insert(),
                                                    typeID=blueprint_id,
                                                    activityID=activityIDs[activity],
                                                    skillID=skill['typeID'],
                                                    level=skill['level'])
                    except:
                        print('{} has a bad skill'.format(blueprint_id))
    trans.commit()
