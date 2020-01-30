# -*- coding: utf-8 -*-
import sys
import os
import importlib
importlib.reload(sys)
from sqlalchemy import Table

from yaml import load,dump
try:
	from yaml import CSafeLoader as SafeLoader
	print("Using CSafeLoader")
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")


distribution={'twosome':1,'bubble':2}
effectcategory={}


def importyaml(connection,metadata,sourcePath,language='en'):
    print("Importing dogma effects")
    dgmEffects = Table('dgmEffects',metadata)
    
    print("opening Yaml")
        
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','dogmaEffects.yaml'),'r') as yamlstream:
        print("importing")
        dogmaEffects=load(yamlstream,Loader=SafeLoader)
        print("Yaml Processed into memory")
        for dogmaEffectsid in dogmaEffects:
            for effect in dogmaEffects[dogmaEffectsid]:
                connection.execute(dgmEffects.insert(),
                                effectID=dogmaEffectsid,
                                effectName=effect['effectName'],
                                effectCategory=effectcategory.get(effect['effectCategory']),
                                description=effect['descriptionID'][language],
                                guid=effect['guid'],
                                iconID=effect.get['iconID'],
                                isOffensive=effect['isOffensive'],
                                isAssistance=effect['isAssistance'],
                                durationAttributeID=effect.get('durationAttributeID'),
                                trackingSpeedAttributeID=effect.get('trackingSpeedAttributeID'),
                                dischargeAttributeID=effect.get('dischargeAttributeID'),
                                rangeAttributeID=effect.get('rangeAttributeID'),
                                falloffAttributeID=effect.get('falloffAttributeID'),
                                disallowAutoRepeat=effect.get('disallowAutoRepeat'),
                                published=effect.get('published'),
                                displayName=effect.get('displayNameID',[]).get(language),
                                isWarpSafe=effect.get('isWarpSafe'),
                                rangeChance=effect.get('rangeChance'),
                                electronicChance=effect.get('electronicChance'),
                                propulsionChance=effect.get('propulsionChance'),
                                distribution=distribution.get(effect.get('distribution')),
                                sfxName=effect.get('sfxName'),
                                npcUsageChanceAttributeID=effect.get('npcUsageChanceAttributeID'),
                                npcActivationChanceAttributeID=effect.get('npcActivationChanceAttributeID'),
                                fittingUsageChanceAttributeID=effect.get('fittingUsageChanceAttributeID'),
                                modifierInfo=dump(effect.get('modifierInfo'))
                                
                )
    trans.commit()
