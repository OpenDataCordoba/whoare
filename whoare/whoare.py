import logging
import subprocess

from whoare.base import Domain
from whoare.exceptions import ZoneNotFoundError, WhoIsCommandError

logger = logging.getLogger(__name__)


class WhoAre:

    child = None  # the real child object
    domain = None  # Domain Object
    registrant = None  # Registrant Objects
    dnss = []  # all DNSs objects

    def detect_subclass(self, zone):
        subcalsses = WhoAre.__subclasses__()
        logger.info(f'Detecting subclass for {zone} at {subcalsses}')
        
        for cls in WhoAre.__subclasses__():
            logger.info(f'Searching zones for {cls} {cls.zones()}')
            if zone in cls.zones():
                return cls

        error = f'Zone not covered "{zone}"'
        logger.error(error)
        raise ZoneNotFoundError(error)

    def load(self, domain, host=None):
        """ load domain data. 
                domain is DOMAIN.ZONE (never use subdomain like www or others)
                host could be "whois.nic.ar" of rargentina (optional) 
            Return a dict with parsed data and fill class properties """
        
        logger.info(f'Load {domain} {host}')
        
        domain_name, zone = self.detect_zone(domain)
        zone_class = self.detect_subclass(zone)
        self.child = zone_class()
        self.domain = Domain(domain_name, zone)

        logger.info(f'Zone Class {zone_class} {domain_name} {zone}')
        
        domain = f'{domain_name}.{zone}'

        if host:
            command = ['whois', f'-h {host}', domain]
        else:
            command = ['whois', domain]

        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        r = p.communicate()[0]
        raw = r.decode()
        
        if p.returncode != 0:
            error = f'WhoIs error {p.returncode} {raw}'
            logger.error(error)
            raise WhoIsCommandError(error)
            
        self.child.parse(raw)       

    def detect_zone(self, domain):
        logger.info(f'Detect zone {domain}')
        
        domain = domain.lower().strip()

        parts = domain.split('.')
        if parts[0].startswith('https://'):
            parts[0].replace('https://', '')
        elif parts[0].startswith('http://'):
            parts[0].replace('http://', '')

        domain = parts[0]
        zone = '.'.join(parts[1:])

        return domain, zone
