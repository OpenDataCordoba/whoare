import logging
import subprocess
from whoare.zone_parsers.ar.who import WhoAr

logger = logging.getLogger(__name__)

subclasses = [
    WhoAr
]

class Domain:
    
    def __init__(self, base_name, zone):
        logger.info(f'Domain object created {base_name}, {zone}')
        self.base_name = base_name.lower().strip()
        self.zone = zone.lower().strip()
        self.registered = None
        self.changed = None
        self.expire = None
        self.is_free = True  # change is registered

    
    def full_name(self):
        return f'{self.base_name}.{self.zone}'

class Registrant:
    
    def __init__(self, name, legal_uid):
        logger.info(f'Registrant object created {name}, {legal_uid}')
        self.name = name.lower().strip()
        self.legal_uid = legal_uid.lower().strip()
        self.created = None
        self.changed = None


class DNS:
    
    def __init__(self, name):
        logger.info(f'DNS object created {name}')
        self.name = name.lower().strip()
    