import os
import configparser
import requests
from requests_cache import CachedSession
import sqlalchemy as sa
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed

from tqdm import tqdm
import sys


def getgroups(grouplist):
    groupfuture = []
    print("getgroups")
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
            item = itemjson.get('group_id')
            if int(item) in sdegrouplist:
                try:
                    connection.execute(invGroups.update().where(invGroups.c.groupID == sa.literal_column(str(item))),
                                       groupID=item,
                                       groupName=itemjson['name'],
                                       categoryID=itemjson.get('category_id', None),
                                       published=itemjson.get('published', False),
                                       )
                except:
                    pass
            else:
                connection.execute(invGroups.insert().values(
                                   groupID=item,
                                   groupName=itemjson['name'],
                                   categoryID=itemjson.get('category_id', None),
                                   published=itemjson.get('published', False),
                                   ))
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


invGroups = sa.Table('invGroups', metadata, autoload_with=engine, schema=schema)


maingrouplist = []

groupurl = "https://esi.evetech.net/latest/universe/groups/?datasource=tranquility&page={}"


grouplookupurl = 'https://esi.evetech.net/latest/universe/groups/{}/'

errorcount = 0

base_session = CachedSession("evesde", backend="redis")


lookup = sa.select(invGroups)
result = connection.execute(lookup).fetchall()

sdegrouplist = []

for groupdata in result:
    sdegrouplist.append(groupdata.groupID)

reqs_num_workers = 25

session = FuturesSession(max_workers=reqs_num_workers, session=base_session)

page = 1

groups = requests.get(groupurl.format(page))

page += 1

groupjson = groups.json()

maingrouplist = maingrouplist + groupjson

maxpage = int(groups.headers['x-pages'])

pbar = tqdm(total=maxpage)

while page <= maxpage:
    groups = requests.get(groupurl.format(page))
    page += 1
    pbar.update(1)
    groupjson = groups.json()
    maingrouplist = maingrouplist + groupjson

print(f"Page variable is {page}")

firstbadlist = getgroups(maingrouplist)
print("Getting badlist")
secondbadlist = getgroups(firstbadlist)


trans.commit()
