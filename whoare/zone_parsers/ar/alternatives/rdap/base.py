from datetime import datetime
import logging
import pytz
import requests

logger = logging.getLogger(__name__)
tz = pytz.timezone('America/Argentina/Cordoba')


class ArNicRdap:
    """ get domains data via RDAP API: https://rdap.nic.ar/
        """
    def __init__(self):
        self.base_domain = 'https://rdap.nic.ar'
        self.ua = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    
    def get_headers(self):
        return {'User-Agent': self.ua}

    def get_domain(self, domain):
        """ get info about one domain """
        resp = requests.get(f'{self.base_domain}/domain/{domain}', headers=self.get_headers())
        # 404 for free domains
        if resp.status_code == 404:
            return {'is_free': True}

        try:
            data = resp.json()
        except Exception as e:
            logger.error(f'Unable to parse {domain} domain data {e}')
            return None

        # basic tests
        if data['handle'] != domain or data['ldhName'] != domain:
            logger.error(f"Unexpected name for {domain}: {data['handle']} or {data['ldhName']}")
            return None

        data['main_entity'] = self.get_main_entity(data)
        data['main_registrant'] = self.get_entity(data['main_entity']['handle'])

        return data

    def get_main_entity(self, data):
        """ get the main entity for a domain """

        entities = data.get('entities', [])
        if len(entities) != 2:
            logger.error(f'Unexpected entities count for {data["handle"]}')
        for entity in entities:
            if 'registrant' in entity.get('roles', []):
                return entity

    def get_entity(self, uid):
        """ get an entity using the unique ID """

        resp = requests.get(f'{self.base_domain}/entity/{uid}', headers=self.get_headers())
        try:
            data = resp.json()
        except Exception as e:
            logger.error(f'Unable to parse {uid} registrant data {e}')
            return None

        # basic tests
        if data['handle'] != uid:
            logger.error(f"Unexpected handle for {uid}: {data['handle']}")
            return None

        return data
        
    def parse(self, parent):
        """ parse domain coming from main base class 
            parent is a WhoAre object"""
        
        from whoare.base import Domain, Registrant, DNS
        logger.debug(f'Parsing from {__name__}')
        
        domain = parent.domain.full_name()
        data = self.get_domain(domain)
        
        if data.get('is_free', False):
            parent.domain.is_free = True
            return
        
        events = data.get('events', [])
        for event in events:
            if event['eventAction'] == 'registration':
                parent.domain.registered = self._get_nic_date(event['eventDate'])
            elif event['eventAction'] == 'expiration':
                parent.domain.expire = self._get_nic_date(event['eventDate'])
            elif event['eventAction'] == 'last changed':
                parent.domain.changed = self._get_nic_date(event['eventDate'])
        
        mr = data['main_registrant']
        mr_name = None
        for vcard in mr['vcardArray']:
            if 'fn' in vcard:
                mr_name = vcard['text']

        if mr_name is None:
            raise UnexpectedParseError(f'No registrant name in {mr["vcardArray"]}')

        parent.registrant = Registrant(name=mr_name, legal_uid=mr['handle'])

        events = mr.get('events', [])
        for event in events:
            if event['eventAction'] == 'registration':
                parent.registrant.created = self._get_nic_date(event['eventDate'])
            elif event['eventAction'] == 'last changed':
                parent.registrant.changed = self._get_nic_date(event['eventDate'])

        
        nameservers = data.get('nameservers', [])
        for ns in nameservers:
            name = ns['handle']  # also at ['ldhName'] TODO, define better
            logger.info(f'DNS found {name}')
            parent.dnss.append(DNS(name=name))
            
    def _get_nic_date(self, date_str):
        """ nic devuelve distinto aque que en whois \_(-_-)_/ """
        
        try:
            res = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            res = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

        res = tz.localize(res, is_dst=True)        
        # logger.debug(f'_get_nic_date {date_str} {res}')
        return res