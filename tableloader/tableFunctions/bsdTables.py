import sys
import os
import glob
import sqlalchemy
import sqlalchemy.exc
#from sqlalchemy import Table

from yaml import load
try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")

def importyaml(connection: sqlalchemy.Connection, metadata: sqlalchemy.MetaData, sourcePath: os.PathLike):

    print("Importing BSD Tables")

    files=glob.glob(os.path.join(sourcePath,'bsd','*.yaml'))
    for file in files:
        head, tail = os.path.split(file)
        tablename=tail.split('.')[0]

        if tablename[:3] == 'dgm':
            print(f"Skipping {tablename}")
            continue

        print(tablename)
        tablevar = sqlalchemy.Table(tablename, metadata, autoload_with=connection)
        print(f"Importing {file}")
        trans = connection.begin()
        with open(file) as yamlstream:
            print(f"importing {os.path.basename(yamlstream.name)}")
            rows=load(yamlstream,Loader=SafeLoader)
            print(f"{os.path.basename(yamlstream.name)} loaded")
            if rows is not None:
                for row in rows:
                    try:
                        connection.execute(tablevar.insert().values(row))
                    except sqlalchemy.exc.IntegrityError as err:
                        print(f"{tablename} skipped {row} ({err})")
        trans.commit()
