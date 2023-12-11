import sys
import os
from sqlalchemy import Table

from yaml import load
try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")


def importyaml(connection,metadata,sourcePath):
    certCerts = Table('certCerts',metadata)
    certSkills = Table('certSkills',metadata,)
    skillmap={"basic":0,"standard":1,"improved":2,"advanced":3,"elite":4}

    print("Importing Certificates")
    with open(os.path.join(sourcePath,'fsd','certificates.yaml')) as yamlstream:
        print(f"importing {os.path.basename(yamlstream.name)}")
        trans = connection.begin()
        certificates=load(yamlstream,Loader=SafeLoader)
        print(f"{os.path.basename(yamlstream.name)} loaded")
        for certificate in certificates:
            connection.execute(certCerts.insert().values(
                            certID=certificate,
                            name=certificates[certificate].get('name',''),
                            description=certificates[certificate].get('description',''),
                            groupID=certificates[certificate].get('groupID')))
            for skill in certificates[certificate]['skillTypes']:
                for skillLevel in certificates[certificate]['skillTypes'][skill]:
                    connection.execute(certSkills.insert().values(
                                        certID=certificate,
                                        skillID=skill,
                                        certLevelInt=skillmap[skillLevel],
                                        certLevelText=skillLevel,
                                        skillLevel=certificates[certificate]['skillTypes'][skill][skillLevel]
                                        ))
    trans.commit()
