A data loader, to bring in the YAML version of the SDE

Loads data back into approximately the same structure.

Fetch the [YAML SDE from CCP's Developer site](https://developers.eveonline.com/resource/resources).

# Installation

## macOS

Remember to install libyaml first, and adjust the include path for clang:

    sudo port install libyaml
    export C_INCLUDE_PATH=/opt/local/include

or
    brew install libyaml
    export C_INCLUDE_PATH=/opt/local/include (not sure what Homebrew path would be)

For PostgreSQL, you will also need:

    brew install psycopg2

## Ubunutu 20

    sudo update
    sudo -y dist-upgrade
    sudo install -y build-essential
    sudo install -y unzip
    sudo install -y python3.8-full python3.8-dev
    sudo install -y redis-server
    sudo install -y mysql-server
    sudo install -y postgresql postgresql-contrib libpq-dev

# Operation

Alter the settings in sdeloader.cfg, specifically the DSN/URI for the database you'll be using, and the source path for the SDE files.

For MariaDB you want to use ```?charset=utf8mb4``` and for postgresq you want to use ```?client_encoding=utf8```.

Make sure to copy the two csv files to the place you've stuck the SDE.



Then run the loader:

    python Load.py «database engine»

# Database Engines Setup

## MySQL

    $ mysql -u root -p
	mysql> create database evesde;
    mysql> create user 'evesde'@'localhost' identified by 'evesde';
	mysql> grant all privileges on evesde.* to 'evesde'@'%' ;
	mysql> grant all privileges on evesde.* to 'evesde'@'localhost';
	mysql> flush privileges;
    mysql> \q

## PostgreSQL

    $ sudo -i -u postgres
    $ createuser --pwprompt evesde
    $ createdb --owner=evesde --encoding=utf8 evesde
    $ echo "CREATE SCHEMA IF NOT EXISTS evesde AUTHORIZATION evesde;" | psql

## PostgresSQL with Schema

You must create the "evesde" schema before using the loader.
