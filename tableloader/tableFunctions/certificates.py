# -*- coding: utf-8 -*-
import os

from utils import yaml_stream

from sqlalchemy import Table

def load(connection, metadata, sourcePath):

    certCerts = Table('certCerts',metadata)
    certSkills = Table('certSkills',metadata,)

    skillmap={"basic":0,"standard":1,"improved":2,"advanced":3,"elite":4}

    print("Importing Certificates")

    trans = connection.begin()

    with open(os.path.join(sourcePath,'fsd','certificates.yaml'),'r') as yamlstream:
        for certificate in yaml_stream.read_by_any(yamlstream):
            for certificate_id, certificate_details in certificate.items():
                test = 1
                connection.execute(certCerts.insert(),
                                certID=certificate_id,
                                name=certificate_details.get('name',''),
                                description=certificate_details.get('description',''),
                                groupID=certificate_details.get('groupID'))
                for skill in certificate_details['skillTypes']:
                    for skillLevel in certificate_details['skillTypes'][skill]:
                        connection.execute(certSkills.insert(),
                                            certID=certificate_id,
                                            skillID=skill,
                                            certLevelInt=skillmap[skillLevel],
                                            certLevelText=skillLevel,
                                            skillLevel=certificate_details['skillTypes'][skill][skillLevel]
                                            )
    trans.commit()
