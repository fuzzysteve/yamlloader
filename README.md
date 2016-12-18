A data loader, to bring in the YAML version of the SDE

Loads data back into approximately the same structure.

# Installation

## macOS

Remember to install libyaml first, and adjust the include path for clang:

    sudo port install libyaml
    export C_INCLUDE_PATH=/opt/local/include

or

    brew install libyaml
    export C_INCLUDE_PATH=/usr/local/include

For PostgreSQL, you will also need to install `psycopg2`.

# Database Engines

## PostgresSQL with Schema

You must create the "evesde" schema before using the loader.
