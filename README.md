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

For PostgreSQL, you will also need to install `psycopg2`.

# Operation

Alter the settings in ```sdeloader.cfg```, specifically the DSN/URI for the database you'll be using, and the source path for the SDE files. For MariaDB you want to use ```?charset=utf8mb4``` and for postgresq you want to use ```?client_encoding=utf8```.

Make sure to copy the two csv files (```invVolumes1.csv```, ```invVolumes2.csv```) from the repository directory to the sourcePath defined in ```sdeloader.cfg```.



Then run the loader:

    python Load.py «database engine»

# Database Engines

## PostgresSQL with Schema

You must create the "evesde" schema before using the loader.
