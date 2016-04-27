from tableloader.tables import metadata
from sqlalchemy import create_engine
import warnings

warnings.filterwarnings('ignore', '^Unicode type received non-unicode bind param value')

from tableloader.tableFunctions import *

import ConfigParser, os
fileLocation = os.path.dirname(os.path.realpath(__file__))
inifile=fileLocation+'/sdeloader.cfg'
config = ConfigParser.ConfigParser()
config.read(inifile)
destination=config.get('Database','destination')
sourcePath=config.get('Files','sourcePath')

print "connecting to DB"


engine = create_engine(destination)
connection = engine.connect()

print "Creating Tables"

metadata.drop_all(engine,checkfirst=True)
metadata.create_all(engine,checkfirst=True)

print "created"

import tableloader.tableFunctions

blueprints.importyaml(connection,metadata,sourcePath)
categories.importyaml(connection,metadata,sourcePath)
certificates.importyaml(connection,metadata,sourcePath)
graphics.importyaml(connection,metadata,sourcePath)
groups.importyaml(connection,metadata,sourcePath)
icons.importyaml(connection,metadata,sourcePath)
skins.importyaml(connection,metadata,sourcePath)
types.importyaml(connection,metadata,sourcePath)
bsdTables.importyaml(connection,metadata,sourcePath)
universe.importyaml(connection,metadata,sourcePath)