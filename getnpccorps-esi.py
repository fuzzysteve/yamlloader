import os
import configparser
import requests
import sqlalchemy as sa
from requests_cache import CachedSession
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed

from tqdm import tqdm
import sys


def getcorps(corplist):
    corpfuture = []
    print("get corps")
    for corpid in corplist:
        if isinstance(corpid, str) and corpid.startswith("https"):
            corpfuture.append(session.get(str(corpid)))
        else:
            corpfuture.append(session.get(corplookupurl.format(corpid)))
    badlist = []
    pbar = tqdm(total=len(corplist))
    for corpdata in as_completed(corpfuture):
        if corpdata.result().status_code == 200:
            corpid = int(str(corpdata.result().url).split('/')[5])
            corpjson = corpdata.result().json()
            connection.execute(invNames.insert().values(
                               itemID=corpid,
                               itemName=corpjson.get('name', None)
                               ))

            connection.execute(crpNPCCorporations.insert().values(
                               corporationID=corpid,
                               description=corpjson.get('description', None),
                               ))
        else:
            badlist.append(corpdata.result().url)
            print(corpdata.result().url)
        pbar.update(1)
    return badlist


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
redis_server = config.get('Redis', 'server')
redis_db = config.get('Redis', 'db')


schema = None
if database == "postgresschema":
    schema = "evesde"


engine = sa.create_engine(destination, echo=False)
metadata = sa.MetaData(schema=schema)
connection = engine.connect()
trans = connection.begin()


crpNPCCorporations = sa.Table('crpNPCCorporations', metadata, autoload_with=engine, schema=schema)

invNames = sa.Table('invNames', metadata,
                    sa.Column('itemID', sa.INTEGER(), primary_key=True, autoincrement=False, nullable=False),
                    sa.Column('itemName', sa.VARCHAR(length=200), nullable=False),
                    schema=schema
                    )


maincorplist = []

corpurl = "https://esi.evetech.net/latest/corporations/npccorps/?datasource=tranquility"


corplookupurl = 'https://esi.evetech.net/latest/corporations/{}/?datasource=tranquility'

errorcount = 0

base_session = CachedSession("evesde", backend="redis")


reqs_num_workers = 50

session = FuturesSession(max_workers=reqs_num_workers, session=base_session)


corps = requests.get(corpurl).json()

firstbadlist = getcorps(corps)
print("Getting badlist")
secondbadlist = getcorps(firstbadlist)


trans.commit()
