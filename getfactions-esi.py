import requests
from sqlalchemy import create_engine,MetaData,Table,Column,INTEGER,FLOAT,VARCHAR,UnicodeText,DECIMAL,Boolean,select,literal_column
#import requests_cache
from requests_futures.sessions import FuturesSession
import requests_futures
from concurrent.futures import as_completed

from tqdm import tqdm
import sys


def getfactions():
    factiondata=requests.get('https://esi.evetech.net/latest/universe/factions/?datasource=tranquility&language=en-us')
    factionjson=factiondata.json()
    for faction in factionjson:
        connection.execute(chrFactions.insert(),
	factionID=faction.get('faction_id'),
	factionName=faction.get('name'),
	description=faction.get('description'),
	solarSystemID=faction.get('solar_system_id'),
	corporationID=faction.get('corporation_id'),
	sizeFactor=faction.get('size_factor'),
	stationCount=faction.get('station_count'),
	stationSystemCount=faction.get('station_system_count'),
	militiaCorporationID=faction.get('militiaCorporationID'),
    )



if len(sys.argv)<2:
    print("Load.py destination")
    exit()


database=sys.argv[1]

if len(sys.argv)==3:
    language=sys.argv[2]
else:
    language='en'

import configparser, os
fileLocation = os.path.dirname(os.path.realpath(__file__))
inifile=fileLocation+'/sdeloader.cfg'
config = configparser.ConfigParser()
config.read(inifile)
destination=config.get('Database',database)
sourcePath=config.get('Files','sourcePath')

schema=None
if database=="postgresschema":
    schema="evesde"





engine = create_engine(destination, echo=False)
metadata = MetaData(schema=schema)
connection = engine.connect()
trans = connection.begin()

chrFactions =  Table('chrFactions', metadata,
        Column('factionID', INTEGER(), primary_key=True, autoincrement=False, nullable=False),
        Column('factionName', VARCHAR(length=100)),
        Column('description', VARCHAR(length=1000)),
        Column('raceIDs', INTEGER()),
        Column('solarSystemID', INTEGER()),
        Column('corporationID', INTEGER()),
        Column('sizeFactor', FLOAT()),
        Column('stationCount', INTEGER()),
        Column('stationSystemCount', INTEGER()),
        Column('militiaCorporationID', INTEGER()),
        Column('iconID', INTEGER()),
        schema=schema
)



getfactions()


trans.commit()

