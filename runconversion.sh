#/bin/bash -l

## this is the script I run to build everything. It will not be directly useful for you. 


set -x
DATE=$(date +%Y%m%d)
SCRIPT_PATH=$(realpath -s ${BASH_SOURCE})
SCRIPT_DIR=$(dirname ${SCRIPT_PATH})
BASE_DIR=${SCRIPT_DIR}/data

SDE_SOURCE="https://eve-static-data-export.s3-eu-west-1.amazonaws.com/tranquility/sde.zip"
SDE_DEST=${BASE_DIR}/sde.zip
SDE_DIR=${BASE_DIR}/sde

OUTPUT_DIR="/home/web/fuzzwork"


[ -d ${BASE_DIR} ] || mkdir -p ${BASE_DIR}
[ -d ${SDE_DIR} ] || mkdir -p ${SDE_DIR}


cd ${BASE_DIR}


SDE_STATUS=$(curl -s -I -o /dev/null -w "%{http_code}" ${SDE_SOURCE})
if [ $SDE_STATUS -eq 404 ]; then
    echo "no file on server"
    exit
fi


if [ -f ${SDE_DEST} ] && ! [ -d ${SDE_DIR} ]; then
	unzip -qq -t ${SDE_DEST} > /dev/null 2>&1
	if [ $? -ne 0 ]; then
		echo "\"${SDE_DEST}\" invalid, downloading replacement"
		rm ${SDE_DEST} ${SDE_DIR}/etag
	fi
fi


SDE_ETAG=$(curl -s -I ${SDE_SOURCE} | grep ETag)
SDE_ETAG_MATCH=0
if [ -f ${SDE_DIR}/etag ]; then
	OLD_ETAG=$(cat ${SDE_DIR}/etag)
	if [ "$SDE_ETAG" == "$OLD_ETAG" ]; then
		SDE_ETAG_MATCH=1
	else
		echo "New ETag: ${SDE_ETAG}"
	fi
fi

if [ ${SDE_ETAG_MATCH} -gt 0 ]; then
	echo "No etag change"
	exit
fi


if [ ${SDE_ETAG_MATCH} -eq 0 ]; then
	echo "downloading \"${SDE_SOURCE}\" to \"${SDE_DEST}\""
	rm -f ${SDE_DEST}
	curl -s -o ${SDE_DEST} ${SDE_SOURCE}
	if [ $? -ne 0 ]; then
		echo "Download failed"
		exit
	fi
	
	if [ -f ${SDE_DEST} ]; then
		echo "unzipping"
		unzip -u -o ${SDE_DEST}
		if [ $? -ne 0 ]; then
			echo "unzip failed"
			exit
		fi
	fi
	echo "$SDE_ETAG" > ${SDE_DIR}/etag
fi


cd ${SDE_DIR}


if [ ! -d ${SDE_DIR}/.git ]; then
    (cd ${SDE_DIR} && git init)
fi

if [ -d ${SDE_DIR}/.git ]; then
	echo "git add"
	git add -A .
	echo "git commit"
	git commit -m "$DATE update"
	git ls-remote >/dev/null 2>&1
	if [ $? = 0 ]; then
		echo "git push"
		git push origin master
	fi
else
	echo "no git repo in \"${SDE_DIR}\". skipping git updates"
fi


if [ ! -d ${BASE_DIR}/env ]; then
	python3 -m venv ${BASE_DIR}/env
	. ${BASE_DIR}/env/bin/activate
	pip install -U pip wheel setuptools
	if [ -r ${SCRIPT_DIR}/requirements.txt ]; then
		pip install -U --prefer-binary -r ${SCRIPT_DIR}/requirements.txt
	fi
	deactivate
fi


if [ -f ${BASE_DIR}/env/bin/activate ]; then
	. ${BASE_DIR}/env/bin/activate
fi


cd ${SCRIPT_DIR}


#for DRIVER in "sqlite" "mysql" "postgres" "postgresschema"; do
for DRIVER in "sqlite" "mysql" "postgres" ; do
	echo "${DRIVER}"
	python Load.py ${DRIVER} >${DRIVER}.log
	python getitems-esi.py ${DRIVER} >>${DRIVER}.log
	python getgroups-esi.py ${DRIVER} >>${DRIVER}.log
	python getmarketgroups-esi.py ${DRIVER} >>${DRIVER}.log
done


python TypesToJson.py >typestojson.log
python exportTypesxlsx.py


if [ -d ${OUTPUT_DIR} ]; then
	echo "exporting"
	cd ${OUTPUT_DIR}/htdocs/dump/
	mkdir sde-$DATE-TRANQUILITY
	cd sde-$DATE-TRANQUILITY/
	mysqldump --default-character-set=utf8 sdeyaml -r sde-$DATE-TRANQUILITY.sql
	cd ../
	tar -cjvf mysql56-sde-$DATE-TRANQUILITY.tbz2 sde-$DATE-TRANQUILITY/sde-$DATE-TRANQUILITY.sql
	rm sde-$DATE-TRANQUILITY/sde-$DATE-TRANQUILITY.sql
	cd sde-$DATE-TRANQUILITY/
	python ${OUTPUT_DIR}/dumptables.py
	${OUTPUT_DIR}/dumptables.sh
	${OUTPUT_DIR}/invtypes.pl
	mv ${SCRIPT_DIR}/eve.db .
	su - postgres -c "pg_dump sdeyaml --format=c -Ox -f postgres-$DATE-TRANQUILITY.dmp"
	mv ~postgres/postgres-$DATE-TRANQUILITY.dmp .
	su - postgres -c "pg_dump sdeyamlschema --format=c -Ox -f postgres-$DATE-TRANQUILITY-schema.dmp --schema=evesde"
	mv  ~postgres/postgres-$DATE-TRANQUILITY-schema.dmp .
	bzip2 *
	mv ${BASE_DIR}/invTypes.xlsx .
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
	mv /tmp/stations.csv ${OUTPUT_DIR}/htdocs/resources/stations.csv
	mv /tmp/marketitems.csv ${OUTPUT_DIR}/htdocs/market/marketitems.csv
	mv /tmp/typeids.csv ${OUTPUT_DIR}/htdocs/resources/typeids.csv
	cd ${OUTPUT_DIR}/htdocs/resources/
	zip -u typeids.zip
	mysqldump sdeyaml | mysql eve
	
	cd ${SCRIPT_DIR}
	python Load.py mssql >mssql.log
	python getitems-esi.py mssql
	python getgroups-esi.py mssql
	cd ${OUTPUT_DIR}/htdocs/dump/sde-$DATE-TRANQUILITY/
	sqlpackage  /action:export /ssn:localhost /sdn:evesde /tf:evesde.bacpac /su:evesde /sp:jsdknopefjsdkfhnotdjfskafjkdgpassword
	cd ..
	rm mssql-latest.bacpac
	ln -s sde-$DATE-TRANQUILITY/evesde.bacpac mssql-latest.bacpac
	md5sum mssql-latest.bacpac > mssql-latest.bacpac.md5
else
	echo "\"${OUTPUT_DIR}\" does not exist, skipping Steve's output section"
fi

