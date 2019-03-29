# -*- coding: utf-8 -*-
import os
import glob

from utils import yaml_stream

from sqlalchemy import Table

def load(connection, metadata, sourcePath):

    print("Importing BSD Tables")

    files=glob.glob(os.path.join(sourcePath,'bsd','*.yaml'))
    for file in files:

        head, tail = os.path.split(file)
        tablename=tail.split('.')[0]
        tablevar = Table(tablename,metadata)
        print("Importing {}".format(file) + ' into ' + tablename)

        with open(file,'r') as yamlstream:

            count = 1

            print("Processing of Yaml starting")
            trans = connection.begin()

            for record in yaml_stream.read_by_list(yamlstream):
                connection.execute(tablevar.insert().values(record))
                print("Imported record {0}".format(count))
                count += 1
            trans.commit()
