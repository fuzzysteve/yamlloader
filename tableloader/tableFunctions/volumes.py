import csv
import os
import sys

import sqlalchemy as sa
import yaml
from sqlalchemy import Table, literal_column, select


def importVolumes(connection: sa.Connection, metadata: sa.MetaData, sourcePath: os.PathLike):

    invVolumes = Table('invVolumes',metadata)
    invTypes = Table('invTypes',metadata)
    with open(os.path.join(sourcePath,'invVolumes1.csv')) as groupVolumes:
        volumereader=csv.reader(groupVolumes, delimiter=',')
        for group in volumereader:
            sel = sa.select(invTypes.c.typeID, literal_column(group[0])).where(invTypes.c.groupID == literal_column(group[1]))
            connection.execute(invVolumes.insert().from_select(['typeID','volume'], sel))
    with open(os.path.join(sourcePath,'invVolumes2.csv')) as groupVolumes:
        volumereader=csv.reader(groupVolumes, delimiter=',')
        for group in volumereader:
            connection.execute(invVolumes.insert().values(typeID=group[1],volume=group[0]))
