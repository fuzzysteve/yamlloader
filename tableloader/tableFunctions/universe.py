# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import glob
import yaml
from sqlalchemy import Table

typeidcache={}

def grouplookup(connection,metadata,typeid):

    if typeidcache.get(typeid):
        return typeidcache.get(typeid)
        
    invTypes =  Table('invTypes', metadata)
    try:
        groupid=connection.execute(
                invTypes.select().where( invTypes.c.typeID == typeid )
            ).fetchall()[0]['groupID']
    except:
        print typeid
        exit()
    typeidcache[typeid]=groupid
    return groupid



def importyaml(connection,metadata,sourcePath):

    print "Importing Universe Data"

    mapCelestialStatistics =  Table('mapCelestialStatistics', metadata) #done
    mapConstellations =  Table('mapConstellations', metadata) # done
    mapDenormalize =  Table('mapDenormalize', metadata) # done
    mapRegions =  Table('mapRegions', metadata) # done
    mapSolarSystems =  Table('mapSolarSystems', metadata) # done
    mapJumps =  Table('mapJumps', metadata) # done

    mapLandmarks =  Table('mapLandmarks', metadata)
    mapLocationScenes =  Table('mapLocationScenes', metadata)
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
        print "Importing Region {}".format(head)
        trans = connection.begin()
        with open(regionfile,'r') as yamlstream:
            region=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
        regionname=connection.execute(
            invNames.select().where( invNames.c.itemID == region['regionID'] )
        ).fetchall()[0]['itemName']
        print "Region {}".format(regionname)
        connection.execute(mapRegions.insert(),
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
                            factionID=region.get('factionID'))
        connection.execute(mapDenormalize.insert(),
                            itemID=region['regionID'],
                            typeID=3,
                            groupID=3,
                            itemName=regionname,
                            x=region['center'][0],
                            y=region['center'][1],
                            z=region['center'][2])
                                        
        connection.execute(mapLocationScenes.insert(),
                            locationID=region['regionID'],
                            graphicID=region['nebula'])
        print "Importing Constellations."
        constellations=glob.glob(os.path.join(head,'*','constellation.staticdata'))
        for constellationfile in constellations:
            chead, tail = os.path.split(constellationfile)
            with open(constellationfile,'r') as yamlstream:
                constellation=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
            constellationname=connection.execute(
                invNames.select().where( invNames.c.itemID == constellation['constellationID'] )
            ).fetchall()[0]['itemName']
            print "Constellation {}".format(constellationname)
            connection.execute(mapConstellations.insert(),
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
                                radius=constellation['radius'])
            connection.execute(mapDenormalize.insert(),
                                itemID=constellation['constellationID'],
                                regionID=region['regionID'],
                                typeID=4,
                                groupID=4,
                                itemName=constellationname,
                                x=region['center'][0],
                                y=region['center'][1],
                                z=region['center'][2])
            systems=glob.glob(os.path.join(chead,'*','solarsystem.staticdata'))
            print "Importing Systems"
            for systemfile in systems:
                with open(systemfile,'r') as yamlstream:
                    system=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
                systemname=connection.execute(
                    invNames.select().where( invNames.c.itemID == system['solarSystemID'] )
                ).fetchall()[0]['itemName']
                print "System {}".format(systemname)
                starname=connection.execute(
                    invNames.select().where( invNames.c.itemID == system['star']['id'] )
                ).fetchall()[0]['itemName']
                connection.execute(mapDenormalize.insert(),
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
                                    security=system['security'])
                if system.get('secondarySun'):
                    connection.execute(mapDenormalize.insert(),
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
                                    security=0)
                                    
                                    
                connection.execute(mapSolarSystems.insert(),
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
                                    factionid=system.get('factionID'),
                                    radius=system['radius'],
                                    sunTypeID=system['sunTypeID'],
                                    securityClass=system.get('securityClass'))
                print "Importing Statistics"
                sstats=system['star'].get('statistics',{})
                sstats['celestialID']=system['star']['id']
                connection.execute(mapCelestialStatistics.insert(),sstats)
                for planet in system.get('planets'):
                    pstats=system['planets'][planet].get('statistics',{})
                    pstats['celestialID']=planet
                    connection.execute(mapCelestialStatistics.insert(),pstats)
                    for belt in system['planets'][planet].get('asteroidBelts',[]):
                        bstats=system['planets'][planet]['asteroidBelts'][belt].get('statistics',{})
                        bstats['celestialID']=belt
                        connection.execute(mapCelestialStatistics.insert(),bstats)
                    for moon in system['planets'][planet].get('moons',[]):
                        mstats=system['planets'][planet]['moons'][moon].get('statistics',{})
                        mstats['celestialID']=moon
                        connection.execute(mapCelestialStatistics.insert(),mstats)
                print "Importing Stargates"
                for stargate in system.get('stargates',[]):
                    jump={'stargateID':stargate,'destinationID':system['stargates'][stargate]['destination']}
                    connection.execute(mapJumps.insert(),jump)
                print "Importing to mapDenormalize"
                connection.execute(mapDenormalize.insert(),
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
                                        security=system['security'])
                for planet in system.get('planets'):
                    planetname=connection.execute(
                        invNames.select().where( invNames.c.itemID == planet )
                        ).fetchall()[0]['itemName']
                    connection.execute(mapDenormalize.insert(),
                                        itemID=planet,
                                        typeID=system['planets'][planet]['typeID'],
                                        groupID=grouplookup(connection,metadata,system['planets'][planet]['typeID']),
                                        solarSystemID=system['solarSystemID'],
                                        constellationID=constellation['constellationID'],
                                        regionID=region['regionID'],
                                        orbitID=system['solarSystemID'],
                                        x=system['planets'][planet]['position'][0],
                                        y=system['planets'][planet]['position'][1],
                                        z=system['planets'][planet]['position'][2],
                                        radius=system['planets'][planet]['radius'],
                                        itemName=planetname,
                                        security=system['security'],
                                        celestialIndex=system['planets'][planet]['celestialIndex'])
                    x=0
                    for belt in system['planets'][planet].get('asteroidBelts',[]):
                        x+=1
                        beltname=connection.execute(
                            invNames.select().where( invNames.c.itemID == belt )
                            ).fetchall()[0]['itemName']
                        connection.execute(mapDenormalize.insert(),
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
                                            orbitIndex=x)
                    for npcstation in system['planets'][planet].get('npcStations',[]):
                            stationname=connection.execute(
                                invNames.select().where( invNames.c.itemID == npcstation )
                                ).fetchall()[0]['itemName']
                            connection.execute(mapDenormalize.insert(),
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
                                                security=system['security'])
                    x=0
                    for moon in system['planets'][planet].get('moons',[]):
                        x+=1
                        moonname=connection.execute(
                            invNames.select().where( invNames.c.itemID == moon )
                            ).fetchall()[0]['itemName']
                        connection.execute(mapDenormalize.insert(),
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
                                            orbitIndex=x)
                        for npcstation in system['planets'][planet]['moons'][moon].get('npcStations',[]):
                            stationname=connection.execute(
                                invNames.select().where( invNames.c.itemID == npcstation )
                                ).fetchall()[0]['itemName']
                            connection.execute(mapDenormalize.insert(),
                                                itemID=npcstation,
                                                typeID=system['planets'][planet]['moons'][moon]['npcStations'][npcstation]['typeID'],
                                                groupID=grouplookup(connection,metadata,system['planets'][planet]['moons'][moon]['npcStations'][npcstation]['typeID']),
                                                solarSystemID=system['solarSystemID'],
                                                constellationID=constellation['constellationID'],
                                                regionID=region['regionID'],
                                                orbitID=planet,
                                                x=system['planets'][planet]['moons'][moon]['npcStations'][npcstation]['position'][0],
                                                y=system['planets'][planet]['moons'][moon]['npcStations'][npcstation]['position'][1],
                                                z=system['planets'][planet]['moons'][moon]['npcStations'][npcstation]['position'][2],
                                                itemName=stationname,
                                                security=system['security'])
                        
                for stargate in system.get('stargates',[]):
                    connection.execute(mapDenormalize.insert(),
                                        itemID=stargate,
                                        typeID=system['stargates'][stargate]['typeID'],
                                        groupID=grouplookup(connection,metadata,system['stargates'][stargate]['typeID']),
                                        solarSystemID=system['solarSystemID'],
                                        constellationID=constellation['constellationID'],
                                        regionID=region['regionID'],
                                        x=system['stargates'][stargate]['position'][0],
                                        y=system['stargates'][stargate]['position'][1],
                                        z=system['stargates'][stargate]['position'][2],
                                        security=system['security'])

        trans.commit()