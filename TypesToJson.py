# -*- coding: utf-8 -*-
import sys
import importlib
importlib.reload(sys)
import yaml
import json
import os
try:
	from yaml import CSafeLoader as SafeLoader
	print("Using CSafeLoader")
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")


import configparser, os
fileLocation = os.path.dirname(os.path.realpath(__file__))
inifile=fileLocation+'/sdeloader.cfg'
config = configparser.ConfigParser()
config.read(inifile)
sourcePath=config.get('Files','sourcePath')
destinationPath=config.get('Files','destinationPath')





print("opening Yaml")
with open(os.path.join(sourcePath,'fsd','typeIDs.yaml'),'r') as yamlstream:
    print("importing")
    typeids=load(yamlstream,Loader=SafeLoader)
    print("Yaml Processed into memory")
    with open(os.path.join(destinationPath,'typeid.json'),"w") as output:
        json.dump(typeids,output)
