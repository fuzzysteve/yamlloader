# -*- coding: utf-8 -*-
import sys
import os
import glob
import sqlalchemy
#from sqlalchemy import Table

from yaml import load
try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")

def importyaml(connection,metadata,sourcePath):

    print("Importing BSD Tables")

    files=glob.glob(os.path.join(sourcePath,'bsd','*.yaml'))
    for file in files:
        head, tail = os.path.split(file)
        tablename=tail.split('.')[0]
        print(tablename)
        tablevar = sqlalchemy.Table(tablename,metadata)
        print("Importing {}".format(file))
        print("Opening Yaml")
        trans = connection.begin()
        with open(file,'r') as yamlstream:
            rows=load(yamlstream,Loader=SafeLoader)
            print("Yaml Processed into memory")
            for row in rows:
                try:
                    connection.execute(tablevar.insert().values(row))
                except sqlalchemy.exc.IntegrityError as err:
                    print("{} skipped {} ({})".format(tablename, row, err))
        trans.commit()

