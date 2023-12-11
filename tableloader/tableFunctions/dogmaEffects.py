import sys
import os
from sqlalchemy import Table

from yaml import load,dump
try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")


distribution={'twosome':1,'bubble':2}
effectcategory={}


def importyaml(connection,metadata,sourcePath,language='en'):
    print("Importing dogma effects")
    dgmEffects = Table('dgmEffects',metadata)
    
    trans = connection.begin()
    with open(os.path.join(sourcePath,'fsd','dogmaEffects.yaml')) as yamlstream:
        print(f"importing {os.path.basename(yamlstream.name)}")
        dogmaEffects=load(yamlstream,Loader=SafeLoader)
        print(f"{os.path.basename(yamlstream.name)} loaded")
        for dogmaEffectsid in dogmaEffects:
            effect=dogmaEffects[dogmaEffectsid]
            connection.execute(dgmEffects.insert().values(
                                effectID=dogmaEffectsid,
                                effectName=effect.get('effectName'),
                                effectCategory=effectcategory.get(effect['effectCategory']),
                                description=effect.get('descriptionID',{}).get(language),
                                guid=effect.get('guid'),
                                iconID=effect.get('iconID'),
                                isOffensive=effect['isOffensive'],
                                isAssistance=effect['isAssistance'],
                                durationAttributeID=effect.get('durationAttributeID'),
                                trackingSpeedAttributeID=effect.get('trackingSpeedAttributeID'),
                                dischargeAttributeID=effect.get('dischargeAttributeID'),
                                rangeAttributeID=effect.get('rangeAttributeID'),
                                falloffAttributeID=effect.get('falloffAttributeID'),
                                disallowAutoRepeat=effect.get('disallowAutoRepeat'),
                                published=effect.get('published'),
                                displayName=effect.get('displayNameID',{}).get(language),
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
            ))
    trans.commit()
