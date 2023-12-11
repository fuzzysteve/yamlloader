import sys

from yaml import dump, load

try:
	from yaml import CSafeLoader as SafeLoader
except ImportError:
	from yaml import SafeLoader
	print("Using Python SafeLoader")

import contextlib
import glob
import os

import sqlalchemy as sa
from sqlalchemy import Table, select

typeidcache={}

def grouplookup(connection,metadata,typeid):

    if typeidcache.get(typeid):
        return typeidcache.get(typeid)
        
    invTypes =  Table('invTypes', metadata)
    try:
        groupid=connection.execute(
                sa.select(invTypes.c.groupID)
                .where( invTypes.c.typeID == typeid )
            ).scalar()
    except:
        print(f"Group lookup failed on typeid {typeid}")
        groupid=-1
    typeidcache[typeid]=groupid
    return groupid

def get_distance_squared(c1, c2):
    pos = c1['position']
    mx, my, mz = pos[0], pos[1], pos[2]
    pos = c2['position']
    px, py, pz = pos[0], pos[1], pos[2]
    dx, dy, dz = mx - px, my - py, mz - pz

    return dx * dx + dy * dy + dz * dz

def get_sorted_objects(planet, key):
    with_radius = [(get_distance_squared(obj, planet), obj_id)
                   for (obj_id, obj)
                   in list(planet.get(key, {}).items())]
    with_radius.sort()
    return [obj_id for (radius, obj_id) in with_radius]

def importyaml(connection,metadata,sourcePath):

    print("Importing Universe Data")

    mapCelestialStatistics =  Table('mapCelestialStatistics', metadata) #done
    mapConstellations =  Table('mapConstellations', metadata) # done
    mapDenormalize =  Table('mapDenormalize', metadata) # done
    mapRegions =  Table('mapRegions', metadata) # done
    mapSolarSystems =  Table('mapSolarSystems', metadata) # done
    mapJumps =  Table('mapJumps', metadata) # done
    mapLocationScenes =  Table('mapLocationScenes', metadata) # done
    mapCelestialGraphics =  Table('mapCelestialGraphics', metadata)
    

    mapLandmarks =  Table('mapLandmarks', metadata)
    
    mapLocationWormholeClasses =  Table('mapLocationWormholeClasses', metadata)
    
    # Lookups
    invNames =  Table('invNames', metadata)
    
    # Generated Tables
    mapSolarSystemJumps =  Table('mapSolarSystemJumps', metadata)
    mapConstellationJumps =  Table('mapConstellationJumps', metadata)
    mapRegionJumps =  Table('mapRegionJumps', metadata)
    
    
    
    
    regions=glob.glob(os.path.join(sourcePath,'fsd','universe','*','*','region.staticdata'))
    for regionfile in regions:
        head, tail = os.path.split(regionfile)
        print(f"Importing Region {head}")
        trans = connection.begin()
        with open(regionfile) as yamlstream:
            region=load(yamlstream,Loader=SafeLoader)
        regionname=f"Region #{region['regionID']}"
        with contextlib.suppress(Exception):
            regionname=connection.execute(
                sa.select(invNames.c.itemName)
                .where( invNames.c.itemID == region['regionID'] )
            ).scalar()
        print(f"Region {regionname}")
        connection.execute(mapRegions.insert().values(
                            regionID=region['regionID'],
                            regionName=regionname,
                            x=region['center'][0],
                            y=region['center'][1],
                            z=region['center'][2],
                            xMax=region['max'][0],
                            yMax=region['max'][1],
                            zMax=region['max'][2],
                            xMin=region['min'][0],
                            yMin=region['min'][1],
                            zMin=region['min'][2],
                            nebula=region.get('nebula'),
                            factionID=region.get('factionID')))
        connection.execute(mapDenormalize.insert().values(
                            itemID=region['regionID'],
                            typeID=3,
                            groupID=3,
                            itemName=regionname,
                            x=region['center'][0],
                            y=region['center'][1],
                            z=region['center'][2]))
                                        
        connection.execute(mapLocationScenes.insert().values(
                            locationID=region['regionID'],
                            graphicID=region['nebula']))
                            
        if  region.get('wormholeClassID'):
            connection.execute(mapLocationWormholeClasses.insert().values(
                                locationID=region['regionID'],
                                wormholeClassID=region['wormholeClassID']))
                            
        print("Importing Constellations.")
        constellations=glob.glob(os.path.join(head,'*','constellation.staticdata'))
        for constellationfile in constellations:
            chead, tail = os.path.split(constellationfile)
            with open(constellationfile) as yamlstream:
                constellation=load(yamlstream,Loader=SafeLoader)
            constellationname=f"Constellation #{constellation['constellationID']}"
            with contextlib.suppress(Exception):
                constellationname=connection.execute(
                    sa.select(invNames.c.itemName)
                    .where( invNames.c.itemID == constellation['constellationID'] )
                ).scalar()
            print(f"Constellation {constellationname}")
            connection.execute(mapConstellations.insert().values(
                                regionID=region['regionID'],
                                constellationID=constellation['constellationID'],
                                constellationName=constellationname,
                                x=constellation['center'][0],
                                y=constellation['center'][1],
                                z=constellation['center'][2],
                                xMax=constellation['max'][0],
                                yMax=constellation['max'][1],
                                zMax=constellation['max'][2],
                                xMin=constellation['min'][0],
                                yMin=constellation['min'][1],
                                zMin=constellation['min'][2],
                                radius=constellation['radius'],
                                factionID=constellation.get('factionID',region.get('factionID'))
                                ))
            connection.execute(mapDenormalize.insert().values(
                                itemID=constellation['constellationID'],
                                regionID=region['regionID'],
                                typeID=4,
                                groupID=4,
                                itemName=constellationname,
                                x=constellation['center'][0],
                                y=constellation['center'][1],
                                z=constellation['center'][2]))

            if  constellation.get('wormholeClassID'):
                connection.execute(mapLocationWormholeClasses.insert().values(
                                locationID=constellation['constellationID'],
                                wormholeClassID=constellation['wormholeClassID']))

            systems=glob.glob(os.path.join(chead,'*','solarsystem.staticdata'))
            print("Importing Systems")
            for systemfile in systems:
                with open(systemfile) as yamlstream:
                    system=load(yamlstream,Loader=SafeLoader)
                systemname=f"System #{system['solarSystemID']}"
                with contextlib.suppress(Exception):
                    systemname = connection.execute(
                        sa.select(invNames.c.itemName)
                        .where(invNames.c.itemID == system['solarSystemID'])
                    ).scalar()
                print(f"System {systemname}")
                if 'star' in system:
                    starname = connection.execute(
                        sa.select(invNames.c.itemName)
                        .where(invNames.c.itemID == system['star']['id'])
                    ).scalar()
                    connection.execute(mapDenormalize.insert().values(
                                    itemID=system['star']['id'],
                                    typeID=system['star']['typeID'],
                                    groupID=6,
                                    solarSystemID=system['solarSystemID'],
                                    regionID=region['regionID'],
                                    constellationID=constellation['constellationID'],
                                    x=0,
                                    y=0,
                                    z=0,
                                    radius=system['star']['radius'],
                                    itemName=starname,
                                    security=system['security']))
                if system.get('secondarySun'):
                    connection.execute(mapDenormalize.insert().values(
                                    itemID=system['secondarySun']['itemID'],
                                    typeID=system['secondarySun']['typeID'],
                                    groupID=995,
                                    solarSystemID=system['solarSystemID'],
                                    regionID=region['regionID'],
                                    constellationID=constellation['constellationID'],
                                    x=system['secondarySun']['position'][0],
                                    y=system['secondarySun']['position'][1],
                                    z=system['secondarySun']['position'][2],
                                    itemName='Unknown Anomaly',
                                    security=0))
                                    
                                    
                connection.execute(mapSolarSystems.insert().values(
                                    regionID=region['regionID'],
                                    constellationID=constellation['constellationID'],
                                    solarSystemID=system['solarSystemID'],
                                    solarSystemName=systemname,
                                    x=system['center'][0],
                                    y=system['center'][1],
                                    z=system['center'][2],
                                    xMax=system['max'][0],
                                    yMax=system['max'][1],
                                    zMax=system['max'][2],
                                    xMin=system['min'][0],
                                    yMin=system['min'][1],
                                    zMin=system['min'][2],
                                    luminosity=system['luminosity'],
                                    border=system['border'],
                                    fringe=system['fringe'],
                                    corridor=system['corridor'],
                                    hub=system['hub'],
                                    international=system['international'],
                                    regional=system['regional'],
                                    security=system['security'],
                                    factionID=system.get('factionID',constellation.get('factionID',region.get('factionID'))),
                                    radius=system['radius'],
                                    sunTypeID=system.get('sunTypeID',None),
                                    securityClass=system.get('securityClass')))
                if  system.get('wormholeClassID'):
                    connection.execute(mapLocationWormholeClasses.insert().values(
                                locationID=system['solarSystemID'],
                                wormholeClassID=system['wormholeClassID']))


                print("Importing Statistics")
                if 'star' in system:
                    sstats=system['star'].get('statistics',{})
                    sstats['celestialID']=system['star']['id']
                    connection.execute(mapCelestialStatistics.insert().values(sstats))
                for planet in system.get('planets'):
                    pstats=system['planets'][planet].get('statistics',{})
                    pstats['celestialID']=planet
                    connection.execute(mapCelestialStatistics.insert().values(pstats))
                    for belt in system['planets'][planet].get('asteroidBelts',[]):
                        bstats=system['planets'][planet]['asteroidBelts'][belt].get('statistics',{})
                        bstats['celestialID']=belt
                        connection.execute(mapCelestialStatistics.insert().values(bstats))
                    for moon in system['planets'][planet].get('moons',[]):
                        mstats=system['planets'][planet]['moons'][moon].get('statistics',{})
                        mstats['celestialID']=moon
                        connection.execute(mapCelestialStatistics.insert().values(mstats))


                print("Importing Graphics details")
                for planet in system.get('planets'):
                    pstats=system['planets'][planet].get('planetAttributes',{})
                    pstats['celestialID']=planet
                    connection.execute(mapCelestialGraphics.insert().values(pstats))
                    for moon in system['planets'][planet].get('moons',[]):
                        mstats=system['planets'][planet]['moons'][moon].get('planetAttributes',{})
                        mstats['celestialID']=moon
                        connection.execute(mapCelestialGraphics.insert().values(mstats))


                print("Importing Stargates")
                for stargate in system.get('stargates',[]):
                    jump={'stargateID':stargate,'destinationID':system['stargates'][stargate]['destination']}
                    connection.execute(mapJumps.insert().values(jump))
                print("Importing to mapDenormalize")
                connection.execute(mapDenormalize.insert().values(
                                        itemID=system['solarSystemID'],
                                        typeID=5,
                                        groupID=5,
                                        constellationID=constellation['constellationID'],
                                        regionID=region['regionID'],
                                        x=system['center'][0],
                                        y=system['center'][1],
                                        z=system['center'][2],
                                        radius=system['radius'],
                                        itemName=systemname,
                                        security=system['security']))
                for planet in system.get('planets'):
                    planetname = connection.execute(
                        sa.select(invNames.c.itemName)
                        .where(invNames.c.itemID == planet)
                    ).scalar()
                    connection.execute(mapDenormalize.insert().values(
                                        itemID=planet,
                                        typeID=system['planets'][planet]['typeID'],
                                        groupID=grouplookup(connection,metadata,system['planets'][planet]['typeID']),
                                        solarSystemID=system['solarSystemID'],
                                        constellationID=constellation['constellationID'],
                                        regionID=region['regionID'],
                                        orbitID=system['star']['id'],
                                        x=system['planets'][planet]['position'][0],
                                        y=system['planets'][planet]['position'][1],
                                        z=system['planets'][planet]['position'][2],
                                        radius=system['planets'][planet]['radius'],
                                        itemName=planetname,
                                        security=system['security'],
                                        celestialIndex=system['planets'][planet]['celestialIndex']))
                    x=0
                    for belt in get_sorted_objects(system['planets'][planet], 'asteroidBelts'):
                        x+=1
                        beltname = connection.execute(
                            sa.select(invNames.c.itemName)
                            .where(invNames.c.itemID == belt)
                            ).scalar()
                        connection.execute(mapDenormalize.insert().values(
                                            itemID=belt,
                                            typeID=system['planets'][planet]['asteroidBelts'][belt]['typeID'],
                                            groupID=grouplookup(connection,metadata,system['planets'][planet]['asteroidBelts'][belt]['typeID']),
                                            solarSystemID=system['solarSystemID'],
                                            constellationID=constellation['constellationID'],
                                            regionID=region['regionID'],
                                            orbitID=planet,
                                            x=system['planets'][planet]['asteroidBelts'][belt]['position'][0],
                                            y=system['planets'][planet]['asteroidBelts'][belt]['position'][1],
                                            z=system['planets'][planet]['asteroidBelts'][belt]['position'][2],
                                            radius=1,
                                            itemName=beltname,
                                            security=system['security'],
                                            celestialIndex=system['planets'][planet]['celestialIndex'],
                                            orbitIndex=x))
                    for npcstation in system['planets'][planet].get('npcStations',[]):
                            stationname=connection.execute(
                                sa.select(invNames.c.itemName)
                                .where( invNames.c.itemID == npcstation )
                                ).scalar()
                            connection.execute(mapDenormalize.insert().values(
                                                itemID=npcstation,
                                                typeID=system['planets'][planet]['npcStations'][npcstation]['typeID'],
                                                groupID=grouplookup(connection,metadata,system['planets'][planet]['npcStations'][npcstation]['typeID']),
                                                solarSystemID=system['solarSystemID'],
                                                constellationID=constellation['constellationID'],
                                                regionID=region['regionID'],
                                                orbitID=planet,
                                                x=system['planets'][planet]['npcStations'][npcstation]['position'][0],
                                                y=system['planets'][planet]['npcStations'][npcstation]['position'][1],
                                                z=system['planets'][planet]['npcStations'][npcstation]['position'][2],
                                                itemName=stationname,
                                                security=system['security']))
                    x=0
                    for moon in get_sorted_objects(system['planets'][planet], 'moons'):
                        x+=1
                        moonname=connection.execute(
                            sa.select(invNames.c.itemName)
                            .where( invNames.c.itemID == moon )
                            ).scalar()
                        connection.execute(mapDenormalize.insert().values(
                                            itemID=moon,
                                            typeID=system['planets'][planet]['moons'][moon]['typeID'],
                                            groupID=grouplookup(connection,metadata,system['planets'][planet]['moons'][moon]['typeID']),
                                            solarSystemID=system['solarSystemID'],
                                            constellationID=constellation['constellationID'],
                                            regionID=region['regionID'],
                                            orbitID=planet,
                                            x=system['planets'][planet]['moons'][moon]['position'][0],
                                            y=system['planets'][planet]['moons'][moon]['position'][1],
                                            z=system['planets'][planet]['moons'][moon]['position'][2],
                                            radius=system['planets'][planet]['moons'][moon]['radius'],
                                            itemName=moonname,
                                            security=system['security'],
                                            celestialIndex=system['planets'][planet]['celestialIndex'],
                                            orbitIndex=x))
                        for npcstation in system['planets'][planet]['moons'][moon].get('npcStations',[]):
                            stationname=connection.execute(
                                sa.select(invNames.c.itemName)
                                .where( invNames.c.itemID == npcstation )
                                ).scalar()
                            connection.execute(mapDenormalize.insert().values(
                                                itemID=npcstation,
                                                typeID=system['planets'][planet]['moons'][moon]['npcStations'][npcstation]['typeID'],
                                                groupID=grouplookup(connection,metadata,system['planets'][planet]['moons'][moon]['npcStations'][npcstation]['typeID']),
                                                solarSystemID=system['solarSystemID'],
                                                constellationID=constellation['constellationID'],
                                                regionID=region['regionID'],
                                                orbitID=moon,
                                                x=system['planets'][planet]['moons'][moon]['npcStations'][npcstation]['position'][0],
                                                y=system['planets'][planet]['moons'][moon]['npcStations'][npcstation]['position'][1],
                                                z=system['planets'][planet]['moons'][moon]['npcStations'][npcstation]['position'][2],
                                                itemName=stationname,
                                                security=system['security']))
                        
                for stargate in system.get('stargates',[]):
                    connection.execute(mapDenormalize.insert().values(
                                        itemID=stargate,
                                        typeID=system['stargates'][stargate]['typeID'],
                                        groupID=grouplookup(connection,metadata,system['stargates'][stargate]['typeID']),
                                        solarSystemID=system['solarSystemID'],
                                        constellationID=constellation['constellationID'],
                                        regionID=region['regionID'],
                                        x=system['stargates'][stargate]['position'][0],
                                        y=system['stargates'][stargate]['position'][1],
                                        z=system['stargates'][stargate]['position'][2],
                                        security=system['security']))

        trans.commit()


def buildJumps(connection,connectiontype):

    sql={}
    sql['postgres']=[]
    sql['postgresschema']=[]
    sql['other']=[]

    sql['postgres'].append("""insert into "mapSolarSystemJumps" ("fromRegionID","fromConstellationID","fromSolarSystemID","toRegionID","toConstellationID","toSolarSystemID")
    select f."regionID" "fromRegionID",f."constellationID" "fromConstellationID",f."solarSystemID" "fromSolarSystemID",t."regionID" "toRegionID",t."constellationID" "toConstellationID",t."solarSystemID" "toSolarSystemID"
    from "mapJumps" join "mapDenormalize" f on "mapJumps"."stargateID"=f."itemID" join "mapDenormalize" t on "mapJumps"."destinationID"=t."itemID" """)
    sql['postgres'].append("""insert into "mapRegionJumps"
    select distinct f."regionID",t."regionID"
    from "mapJumps" join "mapDenormalize" f on "mapJumps"."stargateID"=f."itemID" join "mapDenormalize" t on "mapJumps"."destinationID"=t."itemID" where f."regionID"!=t."regionID" """)
    sql['postgres'].append("""insert into "mapConstellationJumps"
    select distinct f."regionID",f."constellationID",t."constellationID",t."regionID"
    from "mapJumps" join "mapDenormalize" f on "mapJumps"."stargateID"=f."itemID" join "mapDenormalize" t on "mapJumps"."destinationID"=t."itemID" where f."constellationID"!=t."constellationID" """)
    sql['postgresschema'].append("""insert into evesde."mapSolarSystemJumps" ("fromRegionID","fromConstellationID","fromSolarSystemID","toRegionID","toConstellationID","toSolarSystemID")
    select f."regionID" "fromRegionID",f."constellationID" "fromConstellationID",f."solarSystemID" "fromSolarSystemID",t."regionID" "toRegionID",t."constellationID" "toConstellationID",t."solarSystemID" "toSolarSystemID"
    from  evesde."mapJumps" join  evesde."mapDenormalize" f on "mapJumps"."stargateID"=f."itemID" join  evesde."mapDenormalize" t on "mapJumps"."destinationID"=t."itemID" """)
    sql['postgresschema'].append("""insert into  evesde."mapRegionJumps"
    select distinct f."regionID",t."regionID"
    from  evesde."mapJumps" join  evesde."mapDenormalize" f on "mapJumps"."stargateID"=f."itemID" join  evesde."mapDenormalize" t on "mapJumps"."destinationID"=t."itemID" where f."regionID"!=t."regionID" """)
    sql['postgresschema'].append("""insert into  evesde."mapConstellationJumps"
    select distinct f."regionID",f."constellationID",t."constellationID",t."regionID"
    from  evesde."mapJumps" join  evesde."mapDenormalize" f on "mapJumps"."stargateID"=f."itemID" join  evesde."mapDenormalize" t on "mapJumps"."destinationID"=t."itemID" where f."constellationID"!=t."constellationID" """)

    sql['other'].append("""insert into mapSolarSystemJumps (fromRegionID,fromConstellationID,fromSolarSystemID,toRegionID,toConstellationID,toSolarSystemID)
    select f.regionID fromRegionID,f.constellationID fromConstellationID,f.solarSystemID fromSolarSystemID,t.regionID toRegionID,t.constellationID toConstellationID,t.solarSystemID toSolarSystemID
    from mapJumps join mapDenormalize f on mapJumps.stargateID=f.itemID join mapDenormalize t on mapJumps.destinationID=t.itemID""")
    sql['other'].append("""insert into mapRegionJumps
    select distinct f.regionID,t.regionID
    from mapJumps join mapDenormalize f on mapJumps.stargateID=f.itemID join mapDenormalize t on mapJumps.destinationID=t.itemID where f.regionID!=t.regionID""")
    sql['other'].append("""insert into mapConstellationJumps
    select distinct f.regionID,f.constellationID,t.constellationID,t.regionID
    from mapJumps join mapDenormalize f on mapJumps.stargateID=f.itemID join mapDenormalize t on mapJumps.destinationID=t.itemID where f.constellationID!=t.constellationID""")

    if connectiontype in ["sqlite", "mysql", "mssql"]:
        connectiontype="other"
    for sql_statment in sql[connectiontype]:
        connection.execute(sa.text(sql_statment))


def fixStationNames(connection,metadata):
    invNames =  Table('invNames', metadata)
    staStations = Table('staStations',metadata)

    connection.execute(staStations.update().values(stationName=sa.select(invNames.c.itemName).where(staStations.c.stationID==invNames.c.itemID).as_scalar()))


