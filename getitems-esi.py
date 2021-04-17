import requests
from sqlalchemy import create_engine,MetaData,Table,Column,INTEGER,FLOAT,VARCHAR,UnicodeText,DECIMAL,Boolean,select,literal_column
#import requests_cache
import redis
import cachecontrol
import cachecontrol.caches.redis_cache
from requests_futures.sessions import FuturesSession
import requests_futures
from concurrent.futures import as_completed

from tqdm import tqdm
import sys


def getitems(typelist):
    typefuture=[]
    print("getitems")
    for typeid in typelist:
        if isinstance(typeid,str) and typeid.startswith("https"):
            typefuture.append(session.get(str(typeid)))
        else:
            typefuture.append(session.get(typelookupurl.format(typeid)))
    badlist=[]
    pbar = tqdm(total=len(typelist))
    for typedata in as_completed(typefuture):
        if typedata.result().status_code==200:
            itemjson=typedata.result().json()
            item=itemjson.get('type_id')
            if int(item) in sdetypelist:
                try:
                    connection.execute(invTypes.update().where(invTypes.c.typeID == literal_column(str(item))),
                               typeID=item,
                               typeName=itemjson['name'],
                               groupID=itemjson.get('group_id',None),
                               marketGroupID=itemjson.get('market_group_id',None),
                               capacity=itemjson.get('capacity',None),
                               published=itemjson.get('published',False),
                               portionSize=itemjson.get('portion_size',None),
                               volume=itemjson.get('volume', None),
                               packagedVolume=itemjson.get('packaged_volume', None)
                               )
                except:
                    pass
            else:
                    connection.execute(invTypes.insert(),
                                typeID=item,
                                typeName=itemjson['name'],
                                marketGroupID=itemjson.get('market_group_id',None),
                                groupID=itemjson.get('group_id',None),
                                published=itemjson.get('published',False),
                                volume=itemjson.get('volume',None),
                                packagedVolume=itemjson.get('packaged_volume', None),
                                capacity=itemjson.get('capacity',None),
                                portionSize=itemjson.get('portion_size',None),
                                mass=itemjson.get('mass',None)
                                )
        else:
            badlist.append(typedata.result().url)
            print(typedata.result().url)
        pbar.update(1)
    return badlist





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
redis_server=config.get('Redis', 'server')
redis_db=config.get('Redis', 'db')

schema=None
if database=="postgresschema":
    schema="evesde"





engine = create_engine(destination, echo=False)
metadata = MetaData(schema=schema)
connection = engine.connect()
trans = connection.begin()



invTypes =  Table('invTypes', metadata,
        Column('typeID', INTEGER(), primary_key=True, autoincrement=False, nullable=False),
        Column('groupID', INTEGER(),index=True),
        Column('typeName', VARCHAR(length=100)),
        Column('description',UnicodeText()),
        Column('mass', FLOAT(precision=53)),
        Column('volume', FLOAT(precision=53)),
        Column('packagedVolume', FLOAT(precision=53)),
        Column('capacity', FLOAT(precision=53)),
        Column('portionSize', INTEGER()),
        Column('raceID', INTEGER()),
        Column('basePrice', DECIMAL(precision=19, scale=4)),
        Column('published', Boolean),
        Column('marketGroupID', INTEGER()),
        Column('iconID', INTEGER()),
        Column('soundID', INTEGER()),
        Column('graphicID', INTEGER()),
        schema=schema,
)


maintypelist=[]

groupurl="https://esi.evetech.net/latest/universe/types/?datasource=tranquility&page={}"



typelookupurl='https://esi.evetech.net/latest/universe/types/{}/'

errorcount=0
#requests_cache.install_cache("item_cache",backend='redis',expire_after=35000)

#base_session=requests_cache.core.CachedSession(cache_name="item_cache",backend='redis',expire_after=35000)
redis_connection = redis.Redis(host=redis_server, db=redis_db, retry_on_timeout=True, health_check_interval=30)
base_session = cachecontrol.CacheControl(requests.session(), cachecontrol.caches.redis_cache.RedisCache(redis_connection))


lookup=select([invTypes])
result=connection.execute(lookup).fetchall()

sdetypelist=[]

for typedata in result:
    sdetypelist.append(typedata.typeID)

reqs_num_workers=25

session = FuturesSession(max_workers=reqs_num_workers,session=base_session)

page=1

groups=requests.get(groupurl.format(page))

page+=1

groupjson=groups.json()

maintypelist=maintypelist+groupjson

maxpage=int(groups.headers['x-pages'])

pbar = tqdm(total=maxpage)

while page<=maxpage:
    groups=requests.get(groupurl.format(page))
    page+=1
    pbar.update(1)
    groupjson=groups.json()
    maintypelist=maintypelist+groupjson

print("Page variable is {}".format(page))

firstbadlist=getitems(maintypelist)
print("Getting badlist")
secondbadlist=getitems(firstbadlist)


trans.commit()

