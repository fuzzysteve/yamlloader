import requests
from sqlalchemy import create_engine,MetaData,Table,Column,INTEGER,FLOAT,VARCHAR,UnicodeText,DECIMAL,Boolean,select,literal_column
import requests_cache
from requests_futures.sessions import FuturesSession
import requests_futures
from concurrent.futures import as_completed

from tqdm import tqdm
import sys


def getgroups(grouplist):
    groupfuture=[]
    print "getgroups"
    for groupid in grouplist:
        if isinstance(groupid,basestring) and groupid.startswith("https"):
            groupfuture.append(session.get(str(groupid)))
        else:
            groupfuture.append(session.get(grouplookupurl.format(groupid)))
    badlist=[]
    pbar = tqdm(total=len(grouplist))
    for groupdata in as_completed(groupfuture):
        if groupdata.result().status_code==200:
            itemjson=groupdata.result().json()
            item=itemjson.get('group_id')
            if int(item) in sdegrouplist:
                try:
                    connection.execute(invGroups.update().where(invGroups.c.groupID == literal_column(str(item))),
                               groupID=item,
                               groupName=itemjson['name'],
                               categoryID=itemjson.get('category_id',None),
                               published=itemjson.get('published',False),
                               )
                except:
                    pass
            else:
                    connection.execute(invGroups.insert(),
                               groupID=item,
                               groupName=itemjson['name'],
                               categoryID=itemjson.get('category_id',None),
                               published=itemjson.get('published',False),
                                )
        else:
            badlist.append(groupdata.result().url)
            print groupdata.result().url
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

schema=None
if database=="postgresschema":
    schema="evesde"





engine = create_engine(destination, echo=False)
metadata = MetaData(schema=schema)
connection = engine.connect()
trans = connection.begin()



invGroups =  Table('invGroups', metadata,
            Column('groupID', INTEGER(), primary_key=True, autoincrement=False, nullable=False),
            Column('categoryID', INTEGER(),index=True),
            Column('groupName', VARCHAR(length=100)),
            Column('iconID', INTEGER()),
            Column('useBasePrice', Boolean(name='invgroup_usebaseprice')),
            Column('anchored', Boolean(name='invgroup_anchored')),
            Column('anchorable', Boolean(name='invgroup_anchorable')),
            Column('fittableNonSingleton', Boolean(name='invgroup_fitnonsingle')),
            Column('published', Boolean(name='invgroup_published')),
            schema=schema
)


maingrouplist=[]

groupurl="https://esi.evetech.net/latest/universe/groups/?datasource=tranquility&page={}"



grouplookupurl='https://esi.evetech.net/latest/universe/groups/{}/'

errorcount=0
requests_cache.install_cache("group_cache",backend='redis',expire_after=35000)

base_session=requests_cache.core.CachedSession(cache_name="item_cache",backend='redis',expire_after=35000)


lookup=select([invGroups])
result=connection.execute(lookup).fetchall()

sdegrouplist=[]

for groupdata in result:
    sdegrouplist.append(groupdata.groupID)

reqs_num_workers=50

session = FuturesSession(max_workers=reqs_num_workers,session=base_session)

page=1

groups=requests.get(groupurl.format(page))

page+=1

groupjson=groups.json()

maingrouplist=maingrouplist+groupjson

maxpage=int(groups.headers['x-pages'])

pbar = tqdm(total=maxpage)

while page<=maxpage:
    groups=requests.get(groupurl.format(page))
    page+=1
    pbar.update(1)
    groupjson=groups.json()
    maingrouplist=maingrouplist+groupjson

print "Page variable is {}".format(page)

firstbadlist=getgroups(maingrouplist)
print "Getting badlist"
secondbadlist=getgroups(firstbadlist)


trans.commit()

