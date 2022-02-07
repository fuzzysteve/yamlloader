import os
import configparser
from tableloader.tables import metadataCreator
from tableloader.tableFunctions import *
import sqlalchemy as sa
import warnings

import sys


warnings.filterwarnings('ignore', '^Unicode type received non-unicode bind param value')


if len(sys.argv) < 2:
    print("Load.py destination")
    exit()


database = sys.argv[1]

if len(sys.argv) == 3:
    language = sys.argv[2]
else:
    language = 'en'

fileLocation = os.path.dirname(os.path.realpath(__file__))
inifile = os.path.join(fileLocation, 'sdeloader.cfg')
config = configparser.ConfigParser()
config.read(inifile)
destination = config.get('Database', database)
sourcePath = config.get('Files', 'sourcePath')


print("connecting to DB")


engine = sa.create_engine(destination)
connection = engine.connect()


schema = None
if database == "postgresschema":
    schema = "evesde"

metadata = metadataCreator(schema)


print("Creating Tables")

metadata.drop_all(engine, checkfirst=True)
metadata.create_all(engine, checkfirst=True)

print("created")

factions.importyaml(connection, metadata, sourcePath, language)
ancestries.importyaml(connection, metadata, sourcePath, language)
bloodlines.importyaml(connection, metadata, sourcePath, language)
npccorporations.importyaml(connection, metadata, sourcePath, language)
characterAttributes.importyaml(connection, metadata, sourcePath, language)
agents.importyaml(connection, metadata, sourcePath, language)
typeMaterials.importyaml(connection, metadata, sourcePath, language)
dogmaTypes.importyaml(connection, metadata, sourcePath, language)
dogmaEffects.importyaml(connection, metadata, sourcePath, language)
dogmaAttributes.importyaml(connection, metadata, sourcePath, language)
dogmaAttributeCategories.importyaml(connection, metadata, sourcePath, language)
blueprints.importyaml(connection, metadata, sourcePath)
marketGroups.importyaml(connection, metadata, sourcePath, language)
metaGroups.importyaml(connection, metadata, sourcePath, language)
controlTowerResources.importyaml(connection, metadata, sourcePath, language)
categories.importyaml(connection, metadata, sourcePath, language)
certificates.importyaml(connection, metadata, sourcePath)
graphics.importyaml(connection, metadata, sourcePath)
groups.importyaml(connection, metadata, sourcePath, language)
icons.importyaml(connection, metadata, sourcePath)
skins.importyaml(connection, metadata, sourcePath)
types.importyaml(connection, metadata, sourcePath, language)
planetary.importyaml(connection, metadata, sourcePath, language)
bsdTables.importyaml(connection, metadata, sourcePath)
universe.importyaml(connection, metadata, sourcePath)
universe.buildJumps(connection, database)
volumes.importVolumes(connection, metadata, fileLocation)
universe.fixStationNames(connection, metadata)
