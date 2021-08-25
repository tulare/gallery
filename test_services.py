# -*- encoding: utf-8 -*-

# Paramètres ligne de commande
import logging

# Configuration
import __main__ as locator
from pk_config import config

from services.web import GrabService

if __name__ == "__main__" :

    # Logging
    logging.basicConfig(level=logging.DEBUG)
    logging.info('start logging')
    
    # Configuration
    prj_database = config.project_database(locator)
    conf = config.Configuration(prj_database)
    
    g = GrabService()
    g.user_agent = conf.get('User-Agent')
    g.ext = ['jpg','jpeg']
    
