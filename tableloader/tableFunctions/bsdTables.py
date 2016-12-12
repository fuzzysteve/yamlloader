# -*- coding: utf-8 -*-
import os
import yaml
from yaml import Loader, SafeLoader
import glob
from sqlalchemy import Table

from yaml import load
try:
	from yaml import CSafeLoader as SafeLoader
	print "Using CSafeLoader"
except ImportError:
	from yaml import SafeLoader
	print "Using Python SafeLoader"

def construct_yaml_str(self, node):
    # Override the default string handling function
    # to always return unicode objects
    return self.construct_scalar(node)
Loader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)
SafeLoader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)


from yaml import load
try:
	from yaml import CSafeLoader as SafeLoader
	print "Using CSafeLoader"
except ImportError:
	from yaml import SafeLoader
	print "Using Python SafeLoader"

def importyaml(connection,metadata,sourcePath):

    print("Importing BSD Tables")

    files=glob.glob(os.path.join(sourcePath,'bsd','*.yaml'))
    for file in files:

        head, tail = os.path.split(file)
        tablename=tail.split('.')[0]
        print(tablename)
        tablevar = Table(tablename,metadata)
        print("Importing {}".format(file))
        print("Opening Yaml")

        with open(file,'r') as yamlstream:

            y = yamlstream.readline()
            cont = 1
            batch = 0
            linecount = 0

            print("Processing of Yaml starting")

            trans = connection.begin()

            while cont:

                l = yamlstream.readline()
                linecount = linecount + 1


                # exits while loop as line is empty
                if len(l) == 0:
                    cont = 0
                else:

                    # add line as part of same section
                    if not l.startswith('-'):
                        y = str(y) + str(l)
                    else:

                        oneYaml = yaml.load(y, Loader=yaml.CSafeLoader)
                        connection.execute(tablevar.insert().values(oneYaml))

                        # start next section concat
                        y = l
                        # add to patch for db insert count
                        batch = batch + 1


                        if batch >= 2000:
                            trans.commit()
                            print("Batch of " + str(batch) + " processed")
                            batch = 0
                            trans = connection.begin()

        trans.commit()
