# -*- coding: utf-8 -*-

import os

from utils import yaml_stream

from sqlalchemy import Table

def load(connection, metadata, sourcePath):

    invTypes        = Table('invTypes',metadata)
    trnTranslations = Table('trnTranslations',metadata)
    certMasteries   = Table('certMasteries',metadata)
    invTraits       = Table('invTraits',metadata)

    print("Importing Types")
    trans = connection.begin()

    with open(os.path.join(sourcePath,'fsd','typeIDs.yaml'),'r') as yamlstream:
        for inv_type in yaml_stream.read_by_any(yamlstream):
            for inv_type_id, inv_type_details in inv_type.items():
                connection.execute(invTypes.insert(),
                                typeID=inv_type_id,
                                groupID=inv_type_details.get('groupID',0),
                                typeName=inv_type_details.get('name',{}).get('en',''),
                                description=inv_type_details.get('description',{}).get('en',''),
                                mass=inv_type_details.get('mass',0),
                                volume=inv_type_details.get('volume',0),
                                capacity=inv_type_details.get('capacity',0),
                                portionSize=inv_type_details.get('portionSize'),
                                raceID=inv_type_details.get('raceID'),
                                basePrice=inv_type_details.get('basePrice'),
                                published=inv_type_details.get('published',0),
                                marketGroupID=inv_type_details.get('marketGroupID'),
                                graphicID=inv_type_details.get('graphicID',0),
                                iconID=inv_type_details.get('iconID'),
                                soundID=inv_type_details.get('soundID'))
                if  "masteries" in inv_type_details:
                    for level in inv_type_details["masteries"]:
                        for cert in inv_type_details["masteries"][level]:
                            connection.execute(certMasteries.insert(),
                                                typeID=inv_type_id,
                                                masteryLevel=level,
                                                certID=cert)
                if ('name' in inv_type_details):
                    for lang in inv_type_details['name']:
                        connection.execute(trnTranslations.insert(),tcID=8,keyID=inv_type_id,languageID=lang,text=inv_type_details['name'][lang])
                if ('description' in inv_type_details):
                    for lang in inv_type_details['description']:
                        connection.execute(trnTranslations.insert(),tcID=33,keyID=inv_type_id,languageID=lang,text=inv_type_details['description'][lang])
                if ('traits' in inv_type_details):
                    if 'types' in inv_type_details['traits']:
                        for skill in inv_type_details['traits']['types']:
                            for trait in inv_type_details['traits']['types'][skill]:
                                result=connection.execute(invTraits.insert(),
                                                    typeID=inv_type_id,
                                                    skillID=skill,
                                                    bonus=trait.get('bonus'),
                                                    bonusText=trait.get('bonusText',{}).get('en',''),
                                                    unitID=trait.get('unitID'))
                                traitid=result.inserted_primary_key
                                for languageid in trait.get('bonusText',{}):
                                    connection.execute(trnTranslations.insert(),tcID=1002,keyID=traitid[0],languageID=languageid,text=trait['bonusText'][languageid])
                    if 'roleBonuses' in inv_type_details['traits']:
                        for trait in inv_type_details['traits']['roleBonuses']:
                            result=connection.execute(invTraits.insert(),
                                    typeID=inv_type_id,
                                    skillID=-1,
                                    bonus=trait.get('bonus'),
                                    bonusText=trait.get('bonusText',{}).get('en',''),
                                    unitID=trait.get('unitID'))
                            traitid=result.inserted_primary_key
                            for languageid in trait.get('bonusText',{}):

                                connection.execute(trnTranslations.insert(),tcID=1002,keyID=traitid[0],languageID=languageid,text=trait['bonusText'][languageid])
                    if 'miscBonuses' in inv_type_details['traits']:
                        for trait in inv_type_details['traits']['miscBonuses']:
                            result=connection.execute(invTraits.insert(),
                                    typeID=inv_type_id,
                                    skillID=-2,
                                    bonus=trait.get('bonus'),
                                    bonusText=trait.get('bonusText',{}).get('en',''),
                                    unitID=trait.get('unitID'))
                            traitid=result.inserted_primary_key
                            for languageid in trait.get('bonusText',{}):
                                connection.execute(trnTranslations.insert(),tcID=1002,keyID=traitid[0],languageID=languageid,text=trait['bonusText'][languageid])
    trans.commit()
