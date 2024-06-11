# -*- coding: utf-8 -*-
from yaml import load, dump
try:
	from yaml import CSafeLoader as SafeLoader
	print "Using CSafeLoader"
except ImportError:
	from yaml import SafeLoader
	print "Using Python SafeLoader"

import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from sqlalchemy import Table

def importyaml(connection,metadata,sourcePath,language='en'):
    invTypes = Table('invTypes',metadata)
    trnTranslations = Table('trnTranslations',metadata)
    certMasteries = Table('certMasteries',metadata)
    invTraits = Table('invTraits',metadata)
    invMetaTypes = Table('invMetaTypes',metadata)
    print "Importing Types"
    print "Opening Yaml"
    with open(os.path.join(sourcePath,'fsd','types.yaml'),'r') as yamlstream:
        trans = connection.begin()
        typeids=load(yamlstream,Loader=SafeLoader)
        print "Yaml Processed into memory"
        for typeid in typeids:
            connection.execute(invTypes.insert(),
                            typeID=typeid,
                            groupID=typeids[typeid].get('groupID',0),
                            typeName=typeids[typeid].get('name',{}).get(language,'').decode('utf-8'),
                            description=typeids[typeid].get('description',{}).get(language,'').decode('utf-8'),
                            mass=typeids[typeid].get('mass',0),
                            volume=typeids[typeid].get('volume',0),
                            capacity=typeids[typeid].get('capacity',0),
                            portionSize=typeids[typeid].get('portionSize'),
                            raceID=typeids[typeid].get('raceID'),
                            basePrice=typeids[typeid].get('basePrice'),
                            published=typeids[typeid].get('published',0),
                            marketGroupID=typeids[typeid].get('marketGroupID'),
                            graphicID=typeids[typeid].get('graphicID',0),
                            iconID=typeids[typeid].get('iconID'),
                            soundID=typeids[typeid].get('soundID'))
            if  typeids[typeid].has_key("masteries"):
                for level in typeids[typeid]["masteries"]:
                    for cert in typeids[typeid]["masteries"][level]:
                        connection.execute(certMasteries.insert(),
                                            typeID=typeid,
                                            masteryLevel=level,
                                            certID=cert)
            if (typeids[typeid].has_key('name')):
                for lang in typeids[typeid]['name']:
                    connection.execute(trnTranslations.insert(),tcID=8,keyID=typeid,languageID=lang.decode('utf-8'),text=typeids[typeid]['name'][lang].decode('utf-8'))
            if (typeids[typeid].has_key('description')):
                for lang in typeids[typeid]['description']:
                    connection.execute(trnTranslations.insert(),tcID=33,keyID=typeid,languageID=lang.decode('utf-8'),text=typeids[typeid]['description'][lang].decode('utf-8'))
            if (typeids[typeid].has_key('traits')):
                if typeids[typeid]['traits'].has_key('types'):
                    for skill in typeids[typeid]['traits']['types']:
                        for trait in typeids[typeid]['traits']['types'][skill]:
                            result=connection.execute(invTraits.insert(),
                                                typeID=typeid,
                                                skillID=skill,
                                                bonus=trait.get('bonus'),
                                                bonusText=trait.get('bonusText',{}).get(language,''),
                                                unitID=trait.get('unitID'))
                            traitid=result.inserted_primary_key
                            for languageid in trait.get('bonusText',{}):
                                connection.execute(trnTranslations.insert(),tcID=1002,keyID=traitid[0],languageID=languageid.decode('utf-8'),text=trait['bonusText'][languageid].decode('utf-8'))
                if typeids[typeid]['traits'].has_key('roleBonuses'):
                    for trait in typeids[typeid]['traits']['roleBonuses']:
                        result=connection.execute(invTraits.insert(),
                                typeID=typeid,
                                skillID=-1,
                                bonus=trait.get('bonus'),
                                bonusText=trait.get('bonusText',{}).get(language,''),
                                unitID=trait.get('unitID'))
                        traitid=result.inserted_primary_key
                        for languageid in trait.get('bonusText',{}):
                            connection.execute(trnTranslations.insert(),tcID=1002,keyID=traitid[0],languageID=languageid.decode('utf-8'),text=trait['bonusText'][languageid].decode('utf-8'))
                if typeids[typeid]['traits'].has_key('miscBonuses'):
                    for trait in typeids[typeid]['traits']['miscBonuses']:
                        result=connection.execute(invTraits.insert(),
                                typeID=typeid,
                                skillID=-2,
                                bonus=trait.get('bonus'),
                                bonusText=trait.get('bonusText',{}).get(language,''),
                                unitID=trait.get('unitID'))
                        traitid=result.inserted_primary_key
                        for languageid in trait.get('bonusText',{}):
                            connection.execute(trnTranslations.insert(),tcID=1002,keyID=traitid[0],languageID=languageid.decode('utf-8'),text=trait['bonusText'][languageid].decode('utf-8'))
            if typeids[typeid].has_key('metaGroupID') or typeids[typeid].has_key('variationParentTypeID'):
                connection.execute(invMetaTypes.insert(),typeID=typeid,metaGroupID=typeids[typeid].get('metaGroupID'),parentTypeID=typeids[typeid].get('variationParentTypeID'))
    trans.commit()
