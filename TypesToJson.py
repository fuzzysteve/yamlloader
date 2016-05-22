# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import pyodbc
import yaml
import json
import os

import ConfigParser, os
fileLocation = os.path.dirname(os.path.realpath(__file__))
inifile=fileLocation+'/sdeloader.cfg'
config = ConfigParser.ConfigParser()
config.read(inifile)
sourcePath=config.get('Files','sourcePath')
destinationPath=config.get('Files','destinationPath')





print "opening Yaml"
with open(os.path.join(sourcePath,'fsd','typeIDs.yaml'),'r') as yamlstream:
    print "importing"
    typeids=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
    print "Yaml Processed into memory"
    with open(os.path.join(destinationPath,'typeid.json'),"w") as output:
        json.dump(typeids,output)
