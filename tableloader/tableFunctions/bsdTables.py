# -*- coding: utf-8 -*-
import os
import yaml
import glob
from sqlalchemy import Table


def importyaml(connection,metadata,sourcePath):

    print "Importing BSD Tables"

    files=glob.glob(os.path.join(sourcePath,'bsd','*.yaml'))
    for file in files:
        head, tail = os.path.split(file)
        tablename=tail.split('.')[0]
        print tablename
        tablevar = Table(tablename,metadata)
        print "Importing {}".format(file)
        print "Opening Yaml"
        trans = connection.begin()
        with open(file,'r') as yamlstream:
            rows=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
            print "Yaml Processed into memory"
            for row in rows:
                connection.execute(tablevar.insert().values(row))
        trans.commit()