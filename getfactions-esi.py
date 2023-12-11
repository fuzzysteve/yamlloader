import sys
import os
import configparser
import requests
import sqlalchemy as sa


def getfactions():
    factiondata = requests.get(
        'https://esi.evetech.net/latest/universe/factions/?datasource=tranquility&language=en-us')
    factionjson = factiondata.json()
    for faction in factionjson:
        connection.execute(chrFactions.insert().values(
                           factionID=faction.get('faction_id'),
                           factionName=faction.get('name'),
                           description=faction.get('description'),
                           solarSystemID=faction.get('solar_system_id'),
                           corporationID=faction.get('corporation_id'),
                           sizeFactor=faction.get('size_factor'),
                           stationCount=faction.get('station_count'),
                           stationSystemCount=faction.get('station_system_count'),
                           militiaCorporationID=faction.get('militiaCorporationID'),
                           ))


if len(sys.argv) < 2:
    print("Load.py destination")
    exit()


database = sys.argv[1]

if len(sys.argv) == 3:
    language = sys.argv[2]
else:
    language = 'en'

fileLocation = os.path.dirname(os.path.realpath(__file__))
inifile = fileLocation + '/sdeloader.cfg'
config = configparser.ConfigParser()
config.read(inifile)
destination = config.get('Database', database)
sourcePath = config.get('Files', 'sourcePath')

schema = None
if database == "postgresschema":
    schema = "evesde"


engine = sa.create_engine(destination, echo=False)
metadata = sa.MetaData(schema=schema)
connection = engine.connect()
trans = connection.begin()

chrFactions = sa.Table('chrFactions', metadata,
                       sa .Column('factionID', sa.INTEGER(), primary_key=True, autoincrement=False, nullable=False),
                       sa.Column('factionName', sa.VARCHAR(length=100)),
                       sa.Column('description', sa.VARCHAR(length=1000)),
                       sa.Column('raceIDs', sa.INTEGER()),
                       sa.Column('solarSystemID', sa.INTEGER()),
                       sa.Column('corporationID', sa.INTEGER()),
                       sa.Column('sizeFactor', sa.FLOAT()),
                       sa.Column('stationCount', sa.INTEGER()),
                       sa.Column('stationSystemCount', sa.INTEGER()),
                       sa.Column('militiaCorporationID', sa.INTEGER()),
                       sa.Column('iconID', sa.INTEGER()),
                       schema=schema
                       )

getfactions()

trans.commit()
