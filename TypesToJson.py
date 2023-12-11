import configparser
import os
import json

import yaml
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader
    print("Using Python SafeLoader")

fileLocation = os.path.dirname(os.path.realpath(__file__))
inifile = fileLocation + '/sdeloader.cfg'
config = configparser.ConfigParser()
config.read(inifile)
sourcePath = config.get('Files', 'sourcePath')
destinationPath = config.get('Files', 'destinationPath')

if not os.path.exists(destinationPath):
    os.makedirs(destinationPath, mode=0o755)

print("opening Yaml")
with open(os.path.join(sourcePath, 'fsd', 'typeIDs.yaml')) as yamlstream:
    print("importing")
    typeids = yaml.load(yamlstream, Loader=SafeLoader)
    print("Yaml Processed into memory")
    with open(os.path.join(destinationPath, 'typeid.json'), "w") as output:
        json.dump(typeids, output)
