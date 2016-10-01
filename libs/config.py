import os

try:
    import ConfigParser
except:
    import configparser as ConfigParser

config = ConfigParser.ConfigParser()

config.read(os.path.join(os.path.dirname(__file__), '..', 'config.ini').replace('\\', '/'))
