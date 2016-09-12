# -*- coding: utf-8 -*-
import os
from sqlalchemy import Table
import yaml

def importyaml(connection,metadata,sourcePath):
    certCerts = Table('certCerts',metadata)
    certSkills = Table('certSkills',metadata,)
    skillmap={"basic":0,"standard":1,"improved":2,"advanced":3,"elite":4}

    print "Importing Certificates"
    print "opening Yaml"
    with open(os.path.join(sourcePath,'fsd','certificates.yaml'),'r') as yamlstream:
        trans = connection.begin()
        certificates=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
        print "Yaml Processed into memory"
        for certificate in certificates:
            connection.execute(certCerts.insert(),
                            certID=certificate,
                            name=certificates[certificate].get('name',''),
                            description=certificates[certificate].get('description',''),
                            groupID=certificates[certificate].get('groupID'))
            for skill in certificates[certificate]['skillTypes']:
                for skillLevel in certificates[certificate]['skillTypes'][skill]:
                    connection.execute(certSkills.insert(),
                                        certID=certificate,
                                        skillID=skill,
                                        certLevelInt=skillmap[skillLevel],
                                        certLevelText=skillLevel,
                                        skillLevel=certificates[certificate]['skillTypes'][skill][skillLevel]
                                        )
    trans.commit()
