import os
import configparser
import requests
import sqlalchemy as sa
from requests_cache import CachedSession
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed

from tqdm import tqdm
import sys


def getgroups(grouplist):
    groupfuture = []
    print("getitems")
    for groupid in grouplist:
        if isinstance(groupid, str) and groupid.startswith("https"):
            groupfuture.append(session.get(str(groupid)))
        else:
            groupfuture.append(session.get(grouplookupurl.format(groupid)))
    badlist = []
    pbar = tqdm(total=len(grouplist))
    for groupdata in as_completed(groupfuture):
        if groupdata.result().status_code == 200:
            itemjson = groupdata.result().json()
            item = itemjson.get('market_group_id')
            if len(itemjson.get('types')):
                hastypes = True
            else:
                hastypes = False
            if int(item) in sdegrouplist:
                try:
                    connection.execute(invMarketGroups.update().where(invMarketGroups.c.marketGroupID == sa.literal_column(str(item))),
                                       marketGroupID=item,
                                       parentGroupID=itemjson.get('parent_group_id'),
                                       marketGroupName=itemjson.get('name'),
                                       description=itemjson.get('description'),
                                       hasTypes=hastypes
                                       )
                except:
                    pass
            else:
                connection.execute(invMarketGroups.insert(),
                                   marketGroupID=item,
                                   parentGroupID=itemjson.get('parent_group_id'),
                                   marketGroupName=itemjson.get('name'),
                                   description=itemjson.get('description'),
                                   hasTypes=hastypes
                                   )
        else:
            badlist.append(groupdata.result().url)
            print(groupdata.result().url)
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
redis_server = config.get('Redis', 'server')
redis_db = config.get('Redis', 'db')

schema = None
if database == "postgresschema":
    schema = "evesde"


engine = sa.create_engine(destination, echo=False)
metadata = sa.MetaData(schema=schema)
connection = engine.connect()
trans = connection.begin()


invMarketGroups = sa.Table('invMarketGroups', metadata,
                           sa.Column('marketGroupID', sa.INTEGER(), primary_key=True, autoincrement=False, nullable=False),
                           sa.Column('parentGroupID', sa.INTEGER()),
                           sa.Column('marketGroupName', sa.VARCHAR(length=100)),
                           sa.Column('description', sa.VARCHAR(length=3000)),
                           sa.Column('iconID', sa.INTEGER()),
                           sa.Column('hasTypes', sa.Boolean(name='invmarketgroups_hastypes')),
                           schema=schema


                           )

maingrouplist = []

groupurl = "https://esi.evetech.net/latest/markets/groups/?datasource=tranquility"


grouplookupurl = 'https://esi.evetech.net/latest/markets/groups/{}/?datasource=tranquility&language=en-us'

errorcount = 0

base_session = CachedSession("evesde", backend="redis")


lookup = sa.select([invMarketGroups])
result = connection.execute(lookup).fetchall()

sdegrouplist = []

for groupdata in result:
    sdegrouplist.append(groupdata.marketGroupID)

reqs_num_workers = 50

session = FuturesSession(max_workers=reqs_num_workers, session=base_session)

page = 1

groups = requests.get(groupurl.format(page))

page += 1

groupjson = groups.json()

maingrouplist = maingrouplist + groupjson

maxpage = int(groups.headers.get('x-pages', 1))

pbar = tqdm(total=maxpage)

while page <= maxpage:
    groups = requests.get(groupurl.format(page))
    page += 1
    pbar.update(1)
    groupjson = groups.json()
    maingrouplist = maingrouplist + groupjson

print("Page variable is {}".format(page))

firstbadlist = getgroups(maingrouplist)
print("Getting badlist")
secondbadlist = getgroups(firstbadlist)


trans.commit()
print("\n\n")
