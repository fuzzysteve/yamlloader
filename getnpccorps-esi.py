import requests
from sqlalchemy import create_engine,MetaData,Table,Column,INTEGER,FLOAT,VARCHAR,UnicodeText,DECIMAL,Boolean,select,literal_column,CHAR
import cachecontrol
import cachecontrol.caches.redis_cache
import redis
from requests_futures.sessions import FuturesSession
import requests_futures
from concurrent.futures import as_completed

from tqdm import tqdm
import sys


def getcorps(corplist):
    corpfuture=[]
    print "get corps"
    for corpid in corplist:
        if isinstance(corpid,basestring) and corpid.startswith("https"):
            corpfputure.append(session.get(str(corpid)))
        else:
            corpfuture.append(session.get(corplookupurl.format(corpid)))
    badlist=[]
    pbar = tqdm(total=len(corplist))
    for corpdata in as_completed(corpfuture):
        if corpdata.result().status_code==200:
            corpid=int(str(corpdata.result().url).split('/')[5])
            corpjson=corpdata.result().json()
            connection.execute(invNames.insert(),
                            itemID=corpid,
                            itemName=corpjson.get('name',None)
            )

            connection.execute(crpNPCCorporations.insert(),
                            corporationID=corpid,
                            description=corpjson.get('description',None),
                            )
        else:
            badlist.append(typedata.result().url)
            print typedata.result().url
        pbar.update(1)
    return badlist





if len(sys.argv)<2:
    print "Load.py destination"
    exit()


database=sys.argv[1]

if len(sys.argv)==3:
    language=sys.argv[2]
else:
    language='en'

import ConfigParser, os
fileLocation = os.path.dirname(os.path.realpath(__file__))
inifile=fileLocation+'/sdeloader.cfg'
config = ConfigParser.ConfigParser()
config.read(inifile)
destination=config.get('Database',database)
sourcePath=config.get('Files','sourcePath')
redis_server=config.get('Redis', 'server')
redis_db=config.get('Redis', 'db')


schema=None
if database=="postgresschema":
    schema="evesde"





engine = create_engine(destination, echo=False)
metadata = MetaData(schema=schema)
connection = engine.connect()
trans = connection.begin()


crpNPCCorporations =  Table('crpNPCCorporations', metadata,
            Column('corporationID', INTEGER(), primary_key=True, autoincrement=False, nullable=False),
            Column('size', CHAR(length=1)),
            Column('extent', CHAR(length=1)),
            Column('solarSystemID', INTEGER()),
            Column('investorID1', INTEGER()),
            Column('investorShares1', INTEGER()),
            Column('investorID2', INTEGER()),
            Column('investorShares2', INTEGER()),
            Column('investorID3', INTEGER()),
            Column('investorShares3', INTEGER()),
            Column('investorID4', INTEGER()),
            Column('investorShares4', INTEGER()),
            Column('friendID', INTEGER()),
            Column('enemyID', INTEGER()),
            Column('publicShares', INTEGER()),
            Column('initialPrice', INTEGER()),
            Column('minSecurity', FLOAT()),
            Column('scattered', Boolean(name='cnpcc_scatt')),
            Column('fringe', INTEGER()),
            Column('corridor', INTEGER()),
            Column('hub', INTEGER()),
            Column('border', INTEGER()),
            Column('factionID', INTEGER()),
            Column('sizeFactor', FLOAT()),
            Column('stationCount', INTEGER()),
            Column('stationSystemCount', INTEGER()),
            Column('description', VARCHAR(length=4000)),
            Column('iconID', INTEGER()),
            schema=schema
            )

invNames =  Table('invNames', metadata,
            Column('itemID', INTEGER(), primary_key=True, autoincrement=False, nullable=False),
            Column('itemName', VARCHAR(length=200), nullable=False),
            schema=schema
    )


maincorplist=[]

corpurl="https://esi.evetech.net/latest/corporations/npccorps/?datasource=tranquility"



corplookupurl='https://esi.evetech.net/latest/corporations/{}/?datasource=tranquility'

errorcount=0

redis_connection = redis.Redis(host=redis_server, db=redis_db, retry_on_timeout=True, health_check_interval=30)
base_session = cachecontrol.CacheControl(requests.session(), cachecontrol.caches.redis_cache.RedisCache(redis_connection))


reqs_num_workers=50

session = FuturesSession(max_workers=reqs_num_workers,session=base_session)


corps=requests.get(corpurl).json()

firstbadlist=getcorps(corps)
print "Getting badlist"
secondbadlist=getcorps(firstbadlist)


trans.commit()

