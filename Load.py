# -*- coding: utf-8 -*-

import sys, io, os

from utils import app_config

from sqlalchemy import create_engine, Table

from tableloader.tables import metadataCreator
from tableloader.tableFunctions import *
import tableloader.tableFunctions

# Fire up application configuration
config = app_config.read()

# Check required parameters
if len(sys.argv)<2:
    print("usage: Load.py destination")
    print("destination must be one of: ("+"|".join(config.options('Database'))+")")
    exit()

database=sys.argv[1]

if len(sys.argv)==3:
    language=sys.argv[2]
else:
    language='en'

destination=config.get('Database',database)
sourcePath=config.get('Files','sourcePath')

print("Connecting to storage engine: " + database)

try:
    engine = create_engine(destination)
    connection = engine.connect()
except Exception as e:
    print(e)
    exit()

schema=None
if database=="postgresschema":
    schema="evesde"

metadata=metadataCreator(schema)

print("Creating Tables")

metadata.drop_all(engine,checkfirst=True)
metadata.create_all(engine,checkfirst=True)

print("Created Tables")

print("Starting yaml imports")

blueprints.load(connection, metadata, sourcePath)
categories.load(connection, metadata, sourcePath, language)
certificates.load(connection, metadata, sourcePath)
graphics.load(connection, metadata, sourcePath)
groups.load(connection, metadata, sourcePath, language)
icons.load(connection, metadata, sourcePath)
skins.load(connection, metadata, sourcePath)
types.load(connection, metadata, sourcePath, language)
bsdTables.load(connection, metadata, sourcePath)
universe.load(connection, metadata, sourcePath)
universe.buildJumps(connection, database)
universe.fixStationNames(connection, metadata)
volumes.importVolumes(connection, metadata, sourcePath)

print("Finished")
