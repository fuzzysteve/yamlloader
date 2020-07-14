#/bin/bash -l

## this is the script I run to build everything. It will not be directly useful for you. 

DATE=`date +%Y%m%d`
cd /opt



STATUS=`curl -s -I -o /dev/null -w "%{http_code}" https://eve-static-data-export.s3-eu-west-1.amazonaws.com/tranquility/sde.zip`
if [ $STATUS -eq 404 ]
   then
    echo "no file on server"
    exit
fi

ETAG=`curl -s -I https://eve-static-data-export.s3-eu-west-1.amazonaws.com/tranquility/sde.zip|grep ETag`

OLDETAG=`cat /opt/sde/etag`

if [ "$ETAG" = "$OLDETAG" ]
   then
    echo "No etag change"
    exit
fi

echo "$ETAG" > /opt/sde/etag

rm /opt/sde.zip


wget https://eve-static-data-export.s3-eu-west-1.amazonaws.com/tranquility/sde.zip

unzip -u -o sde.zip

rm /opt/sde/bsd/dgm*.yaml

cd sde
echo "git add"
git add -A .
echo "git commit"
git commit -m "$DATE update"
echo "git push"
git push origin master

sleep 10

cd /home/scripts/sdeconverter/
. bin/activate
cd yamlloader/

echo "mysql"
python Load.py mysql >mysql.log
echo "sqlite"
python Load.py sqlite >sqlite.log
echo "postgres"
python Load.py postgres >postgres.log
echo "postgres Schema"
python Load.py postgresschema >postgresschema.log
python getitems-esi.py mysql
python getitems-esi.py sqlite
python getitems-esi.py postgres
python getitems-esi.py postgresschema
python getgroups-esi.py mysql
python getgroups-esi.py sqlite
python getgroups-esi.py postgres
python getgroups-esi.py postgresschema


python TypesToJson.py >typestojson.log
python exportTypesxlsx.py


echo "exporting"
cd /home/web/fuzzwork/htdocs/dump/
mkdir sde-$DATE-TRANQUILITY
cd sde-$DATE-TRANQUILITY/
mysqldump --default-character-set=utf8 sdeyaml -r sde-$DATE-TRANQUILITY.sql
cd ../
tar -cjvf mysql56-sde-$DATE-TRANQUILITY.tbz2 sde-$DATE-TRANQUILITY/sde-$DATE-TRANQUILITY.sql
rm sde-$DATE-TRANQUILITY/sde-$DATE-TRANQUILITY.sql
cd sde-$DATE-TRANQUILITY/
python /home/web/fuzzwork/dumptables.py
/home/web/fuzzwork/dumptables.sh
/home/web/fuzzwork/invtypes.pl
mv /home/scripts/sdeconverter/yamlloader/eve.db .
su - postgres -c "pg_dump sdeyaml --format=c -Ox -f postgres-$DATE-TRANQUILITY.dmp"
mv ~postgres/postgres-$DATE-TRANQUILITY.dmp .
su - postgres -c "pg_dump sdeyamlschema --format=c -Ox -f postgres-$DATE-TRANQUILITY-schema.dmp --schema=evesde"
mv  ~postgres/postgres-$DATE-TRANQUILITY-schema.dmp .
bzip2 *
mv /opt/invTypes.xlsx .
cd ../
rm latest mysql-latest.tar.bz2 postgres-latest.dmp.bz2 sqlite-latest.sqlite.bz2 postgres-schema-latest.dmp.bz2
ln -s sde-$DATE-TRANQUILITY latest
ln -s mysql56-sde-$DATE-TRANQUILITY.tbz2 mysql-latest.tar.bz2
ln -s sde-$DATE-TRANQUILITY/eve.db.bz2 sqlite-latest.sqlite.bz2
ln -s sde-$DATE-TRANQUILITY/postgres-$DATE-TRANQUILITY.dmp.bz2 postgres-latest.dmp.bz2
ln -s sde-$DATE-TRANQUILITY/postgres-$DATE-TRANQUILITY-schema.dmp.bz2 postgres-schema-latest.dmp.bz2
md5sum mysql-latest.tar.bz2 >mysql-latest.tar.bz2.md5
md5sum postgres-latest.dmp.bz2 >postgres-latest.dmp.bz2.md5
md5sum sqlite-latest.sqlite.bz2 > sqlite-latest.sqlite.bz2.md5
md5sum postgres-schema-latest.dmp.bz2 > postgres-schema-latest.dmp.bz2.md5

mysql sdeyaml < /root/evesqlfiles/dumpfiles.sql
/bin/mv /tmp/stations.csv /home/web/fuzzwork/htdocs/resources/stations.csv
/bin/mv /tmp/marketitems.csv /home/web/fuzzwork/htdocs/market/marketitems.csv
/bin/mv /tmp/typeids.csv /home/web/fuzzwork/htdocs/resources/typeids.csv
cd /home/web/fuzzwork/htdocs/resources/
zip -u typeids.zip
mysqldump sdeyaml | mysql eve

cd /home/scripts/sdeconverter/yamlloader/
python Load.py mssql >mssql.log
python getitems-esi.py mssql
python getgroups-esi.py mssql
cd /home/web/fuzzwork/htdocs/dump/sde-$DATE-TRANQUILITY/
sqlpackage  /action:export /ssn:localhost /sdn:evesde /tf:evesde.bacpac /su:evesde /sp:jsdknopefjsdkfhnotdjfskafjkdgpassword
cd ..
rm mssql-latest.bacpac
ln -s sde-$DATE-TRANQUILITY/evesde.bacpac mssql-latest.bacpac
md5sum mssql-latest.bacpac > mssql-latest.bacpac.md5

