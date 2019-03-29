# -*- coding: utf-8 -*-
import os

from utils import yaml_stream

from sqlalchemy import Table

def load(connection, metadata, sourcePath):

    eveGraphics = Table('eveGraphics',metadata)

    print("Importing Graphics")

    trans = connection.begin()

    with open(os.path.join(sourcePath,'fsd','graphicIDs.yaml'),'r') as yamlstream:
        for graphic in yaml_stream.read_by_any(yamlstream):
            for graphic_id, graphic_details in graphic.items():
                connection.execute(eveGraphics.insert(),
                                graphicID=graphic_id,
                                sofFactionName=graphic_details.get('sofFactionName',''),
                                graphicFile=graphic_details.get('graphicFile',''),
                                sofHullName=graphic_details.get('sofHullName',''),
                                sofRaceName=graphic_details.get('sofRaceName',''),
                                description=graphic_details.get('description',''))
    trans.commit()
