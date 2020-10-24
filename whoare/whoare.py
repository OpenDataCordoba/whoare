from datetime import datetime
import logging
import subprocess

from whoare.base import Domain, subclasses, Registrant, DNS
from whoare.exceptions import ZoneNotFoundError, WhoIsCommandError

logger = logging.getLogger(__name__)


class WhoAre:

    def __init__(self):
        self.child = None  # the object for the zone
        self.domain = None  # Domain Object
        self.registrant = None  # Registrant Objects
        self.dnss = []  # all DNSs objects
        self.raw_data = None  # whois response

    def get_raw(self, domain, host=None, torify=False):
        if host:
            command = ['whois', f'-h {host}', domain]
        else:
            command = ['whois', domain]
        
        if torify:
            command = ['torify'] + command

        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        r = p.communicate()[0]
        raw = r.decode()
        
        if p.returncode != 0:
            error = f'WhoIs error {p.returncode} {raw}'
            logger.error(error)
            raise WhoIsCommandError(error)
        
        self.raw_data = raw
        return raw

    def load(self, domain, host=None, mock_from_txt_file=None, torify=False):
        """ load domain data. 
                domain is DOMAIN.ZONE (never use subdomain like www or others)
                host could be "whois.nic.ar" of argentina (optional) 
            Return a dict with parsed data and fill class properties 
                mock_from_txt_file could be used to a path with exact whois results """
        
        logger.info(f'Load {domain} {host}')
        
        domain_name, zone = self.detect_zone(domain)
        zone_class = self.detect_subclass(zone)
        self.child = zone_class()
        self.domain = Domain(domain_name, zone)

        logger.info(f'Zone Class {zone_class} {domain_name} {zone}')
        
        domain = f'{domain_name}.{zone}'

        if mock_from_txt_file is not None:
            f = open(mock_from_txt_file)
            raw = f.read()
            f.close()
        else:
            raw = self.get_raw(domain, host, torify)
            
        return self.load_from_raw(raw)

    def load_from_raw(self, raw):

        if self.child.is_free(raw):
            return None

        # raise any errors
        self.child.check_errors(raw)

        self.domain.is_free = False
        # parse raw data
        self.child.parse(raw, self)
        
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
    
    def detect_subclass(self, zone):
        
        logger.info(f'Detecting subclass for {zone} at {subclasses}')
        
        for cls in subclasses:
            logger.info(f'Searching zones for {cls} {cls.zones()}')
            if zone in cls.zones():
                return cls

        error = f'Zone not covered "{zone}"'
        logger.error(error)
        raise ZoneNotFoundError(error)

    def as_dict(self):
        """ build a nice dict """
        res = {
                "domain": {
                    "base_name": self.domain.base_name,
                    "zone": self.domain.zone,
                    "is_free": self.domain.is_free
                    }
                }
        if not self.domain.is_free:
            res["domain"]["registered"] = self.domain.registered.strftime('%Y-%m-%d %H:%M:%S.%f %z')
            res["domain"]["changed"] = self.domain.changed.strftime('%Y-%m-%d %H:%M:%S.%f %z')
            res["domain"]["expire"] = self.domain.expire.strftime('%Y-%m-%d %H:%M:%S.%f %z')
            res["registrant"] = {
                "name": self.registrant.name,
                "legal_uid": self.registrant.legal_uid,
                "created": self.registrant.created.strftime('%Y-%m-%d %H:%M:%S.%f %z'),
                "changed": self.registrant.changed.strftime('%Y-%m-%d %H:%M:%S.%f %z')
                }

            res["dnss"] = [dns.name for dns in self.dnss]
            
        logger.info(f'as dict {res}')
        return res

    def from_dict(self, data):
        """ load object from dict """

        self.domain = Domain(data['domain']['base_name'], data['domain']['zone'])
        self.registrant = None
        self.dnss = []
        self.domain.is_free = data['domain']['is_free']
        if self.domain.is_free:
            return
        
        self.domain.registered = datetime.strptime(data["domain"]["registered"], '%Y-%m-%d %H:%M:%S.%f %z')
        self.domain.changed = datetime.strptime(data["domain"]["changed"], '%Y-%m-%d %H:%M:%S.%f %z')
        self.domain.expire = datetime.strptime(data["domain"]["expire"] , '%Y-%m-%d %H:%M:%S.%f %z')
        
        self.registrant = Registrant(name=data['registrant']['name'], legal_uid=data['registrant']['legal_uid'])
        self.registrant.created = datetime.strptime(data['registrant']['created'], '%Y-%m-%d %H:%M:%S.%f %z')
        self.registrant.changed = datetime.strptime(data['registrant']['changed'], '%Y-%m-%d %H:%M:%S.%f %z')

        for ns in data["dnss"]:
            self.dnss.append(DNS(name=ns))

    def __eq__(self, wa2):
        diffs = []
        if self.domain.base_name != wa2.domain.base_name: 
            diffs.append(f'domain.base_name {self.domain.base_name} != {wa2.domain.base_name}')
        if self.domain.zone != wa2.domain.zone:
            diffs.append(f'domain.zone {self.domain.zone} != {wa2.domain.zone}')
        if self.domain.is_free != wa2.domain.is_free:
            diffs.append('domain.is_free')
        if self.domain.registered != wa2.domain.registered:
            diffs.append(f'domain.registered {self.domain.registered} != {wa2.domain.registered}')
        if self.domain.changed != wa2.domain.changed:
            diffs.append(f'domain.changed {self.domain.changed} != {wa2.domain.changed}')
        if self.domain.expire != wa2.domain.expire:
            diffs.append(f'domain.expire {self.domain.expire} != {wa2.domain.expire}')
        
        if (self.registrant is None) != (wa2.registrant is None):
            diffs.append(f'registrant {self.registrant} != {wa2.registrant}')
        if self.registrant is not None and wa2.registrant is not None:
            if self.registrant.name != wa2.registrant.name:
                diffs.append(f'registrant.name {self.registrant.name} != {wa2.registrant.name}')
            if self.registrant.legal_uid != wa2.registrant.legal_uid:
                diffs.append(f'registrant.legal_uid {self.registrant.legal_uid} != {wa2.registrant.legal_uid}')
            if self.registrant.created != wa2.registrant.created:
                diffs.append(f'registrant.created {self.registrant.created} != {wa2.registrant.created}')
            if self.registrant.changed != wa2.registrant.changed:
                diffs.append(f'registrant.changed {self.registrant.changed} != {wa2.registrant.changed}')
        
        if len(self.dnss) != len(wa2.dnss): 
            diffs.append('Len DNSs')
        else:
            c = 0
            for ns in self.dnss:
                if ns.name != wa2.dnss[c].name:
                    diffs.append(f'DNS {c}. {ns.name} != {wa2.dnss[c].name}')
                c += 1

        logger.info(f'DIFFs {diffs}')
        return len(diffs) == 0

    def as_plain_dict(self):
        """ build a nice dict """
        res = {
            "domain_base_name": self.domain.base_name,
            "domain_zone": self.domain.zone,
            "domain_is_free": self.domain.is_free
            }

        if not self.domain.is_free:
            res["domain_registered"] = self.domain.registered.strftime('%Y-%m-%d %H:%M:%S.%f %z')
            res["domain_changed"] = self.domain.changed.strftime('%Y-%m-%d %H:%M:%S.%f %z')
            res["domain_expire"] = self.domain.expire.strftime('%Y-%m-%d %H:%M:%S.%f %z')
            res["registrant_name"] = self.registrant.name
            res["registrant_legal_uid"] = self.registrant.legal_uid
            res["registrant_created"] = self.registrant.created.strftime('%Y-%m-%d %H:%M:%S.%f %z')
            res["registrant_changed"] = self.registrant.changed.strftime('%Y-%m-%d %H:%M:%S.%f %z')

            c = 1
            for dns in self.dnss:
                res[f"dns{c}"] = dns.name
                c += 1
            
        logger.info(f'as plain dict {res}')
        return res

    def from_plain_dict(self, data):
        """ load object from dict """

        self.domain = Domain(data['domain_base_name'], data['domain_zone'])
        self.registrant = None
        self.dnss = []
        self.domain.is_free = data['domain_is_free']
        if self.domain.is_free:
            return
        
        self.domain.registered = datetime.strptime(data["domain_registered"], '%Y-%m-%d %H:%M:%S.%f %z')
        self.domain.changed = datetime.strptime(data["domain_changed"], '%Y-%m-%d %H:%M:%S.%f %z')
        self.domain.expire = datetime.strptime(data["domain_expire"] , '%Y-%m-%d %H:%M:%S.%f %z')
        
        self.registrant = Registrant(name=data['registrant_name'], legal_uid=data['registrant_legal_uid'])
        self.registrant.created = datetime.strptime(data['registrant_created'], '%Y-%m-%d %H:%M:%S.%f %z')
        self.registrant.changed = datetime.strptime(data['registrant_changed'], '%Y-%m-%d %H:%M:%S.%f %z')

        for c in range(1, 20):
            if f"dns{c}" in data:
                self.dnss.append(DNS(name=data[f"dns{c}"]))
            else:
                break
