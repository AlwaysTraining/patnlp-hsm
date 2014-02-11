"""
Setup application configuration.

Loads default configuration file from `textlab` source package.
Configuration file can be overridden by giving the executable program command line argument.
"""
import ConfigParser
import logging
import sys
import os
import textlab

logging.basicConfig()
logger = logging.getLogger('configuration')
logger.setLevel(logging.DEBUG)

CONF_FILE_PATH = os.path.join(os.path.dirname(textlab.__file__), 'textlab.conf')
logger.info('Setting default config file path to ' + CONF_FILE_PATH)
#if len(sys.argv) == 2:
#    CONF_FILE_PATH = sys.argv[1]
#    logger.info('Overriding default configuration file path. New path is ' + CONF_FILE_PATH)

PACKAGE_PATH = os.path.dirname(os.path.dirname(textlab.__file__))
MODELS_PATH = os.path.join(PACKAGE_PATH, 'models')
DICTIONARY_PATH = os.path.join(MODELS_PATH, 'dictionary')

class StripConfigParser(ConfigParser.RawConfigParser):
    def get(self, section, option):
        val = ConfigParser.RawConfigParser.get(self, section, option)
        val = val.strip().lstrip('"').rstrip('"')
        return val

def get_config():
    '''Function for loading default configuration.'''
    config = StripConfigParser()
    config.readfp(open(CONF_FILE_PATH))
    return config

config = get_config()
