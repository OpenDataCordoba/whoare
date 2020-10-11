import logging
import subprocess


logger = logging.getLogger(__name__)


class Domain:
    base_name = None
    zone = None
    registered = None
    changed = None
    expire = None

    def __init__(self, base_name, zone):
        logger.info(f'Domain object created {base_name}, {zone}')
        self.base_name = base_name.lower().strip()
        self.zone = zone.lower().strip()
    
    def full_name(self):
        return f'{self.base_name}.{self.zone}'

class Registrant:
    legal_uid = None
    name = None
    created = None
    changed = None

    def __init__(self, name, legal_uid):
        logger.info(f'Registrant object created {name}, {legal_uid}')
        self.name = name.lower().strip()
        self.legal_uid = legal_uid.lower().strip()

class DNS:
    name = None

    def __init__(self, name):
        logger.info(f'DNS object created {name}')
        self.name = name.lower().strip()
    