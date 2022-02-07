import os
import configparser
from openpyxl import Workbook
import sqlalchemy


database = 'mysql'

fileLocation = os.path.dirname(os.path.realpath(__file__))
inifile = fileLocation + '/sdeloader.cfg'
config = configparser.ConfigParser()
config.read(inifile)
source = config.get('Database', database)


engine = sqlalchemy.create_engine(source)
connection = engine.connect()


metadata = sqlalchemy.MetaData()
metadata.bind = engine

invtypes = sqlalchemy.Table('invTypes', metadata, autoload=True)

select = sqlalchemy.sql.select([invtypes])

result = connection.execute(select)

wb = Workbook(write_only=True)
ws = wb.create_sheet()
first = True
for row in result:
    if first:
        ws.append(list(row.keys()))
        first = False
    ws.append(list(row))

wb.save('/tmp/invTypes.xlsx')
