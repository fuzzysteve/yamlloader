# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import glob
from sqlalchemy import Table

from yaml import load
try:
	from yaml import CSafeLoader as SafeLoader
	print "Using CSafeLoader"
except ImportError:
	from yaml import SafeLoader
	print "Using Python SafeLoader"

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
            rows=load(yamlstream,Loader=SafeLoader)
            print "Yaml Processed into memory"
            for row in rows:
                connection.execute(tablevar.insert().values(row))
        trans.commit()