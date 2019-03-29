import configparser, os, sys

def read():
    fileLocation = os.path.abspath(os.path.dirname(sys.argv[0]))
    inifile=fileLocation+'/config.cfg'
    config = configparser.ConfigParser()
    config.read(inifile, encoding='utf-8')
    return config
