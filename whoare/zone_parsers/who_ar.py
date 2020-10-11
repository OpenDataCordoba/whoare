from datetime import datetime

from whoare.base import Registrant, DNS
from whoare.whoare import WhoAre
from whoare.exceptions import TooManyQueriesError, ServiceUnavailableError, UnknownError, UnexpectedParseError


class WhoAr(WhoAre):

    @classmethod
    def zones(cls):
        return ['ar', 'com.ar', 'gob.ar', 'gov.ar', 'int.ar', 'mil.ar', 'org.ar']

    def is_free(self, raw):
        """ determine if domain is free """
        return "El dominio no se encuentra registrado" in raw

    def has_error(self, raw):
        
        if "el servicio WHOIS de NIC Argentina se encuentra inactivo" in raw:
            raise ServiceUnavailableError()

        if "Excediste la cantidad permitida de consultas" in raw:
            raise TooManyQueriesError()

        if "fgets: Conexión reinicializada por la máquina remota" in raw:
            raise UnknownError()
        

    def parse(self, raw):

        if self.is_free(raw):
            return None

        self.has_error(raw)

        lines = raw.split('\n')

        # ==========================================
        field, value = self._parse_line(lines[0])
        if field != 'domain':
            raise UnexpectedParseError(f'Field {field} is not "domain"')
        
        if value != self.domain.full_name():
            raise UnexpectedParseError(f'Unexpected domain {value} != {self.domain.full_name()}')
        
        # ==========================================
        field, value = self._parse_line(lines[1])
        if field != 'registrant':
            raise UnexpectedParseError(f'Field {field} is not "registrant"')
        
        registrant_uid = value

        # ignore line 2, registrar

        # ==========================================
        field, value = self._parse_line(lines[3])
        if field != 'registered':
            raise UnexpectedParseError(f'Field {field} is not "registered"')
        
        self.domain.registed = self._get_nic_date(value)
        
        # ==========================================
        field, value = self._parse_line(lines[4])
        if field != 'changed':
            raise UnexpectedParseError(f'Field {field} is not "changed"')

        self.domain.changed = self._get_nic_date(value)
        
        # ==========================================
        field, value = self._parse_line(lines[5])
        if field != 'expire':
            raise UnexpectedParseError(f'Field {field} is not "expire"')

        self.domain.expire = self._get_nic_date(value)
        
        # 6 is empty

        # ==========================================
        field, value = self._parse_line(lines[7])
        if field != 'contact':
            raise UnexpectedParseError(f'Field {field} is not "contact"')

        if value != registrant_uid:
            raise UnexpectedParseError(f'Legal UID diff {value} != {registrant_uid}')

        # ==========================================
        field, value = self._parse_line(lines[8])
        if field != 'name':
            raise UnexpectedParseError(f'Field {field} is not "name"')

        self.registrant = Registrant(name=value, legal_uid=registrant_uid)

        # ignore line 9, registrar

        # ==========================================
        field, value = self._parse_line(lines[10])
        if field != 'created':
            raise UnexpectedParseError(f'Field {field} is not "created"')
        
        self.registrant.created = self._get_nic_date(value)

        # ==========================================
        field, value = self._parse_line(lines[11])
        if field != 'changed':
            raise UnexpectedParseError(f'Field {field} is not "changed"')
        
        self.registrant.changed = self._get_nic_date(value)

        # 12 is empty

        # ==========================================
        field, value = self._parse_line(lines[13])
        n = 13
        while field == "nserver":
            self.dnss.append(DNS(name=value))
            n += 1
            field, value = self._parse_line(lines[n])

        
    def _parse_line(self, line):
        field, value = line.split(':')
        field = field.lower().strip()
        value = value.lower().strip()

        return field, value

    def _get_nic_date(self, date_str):
        """ nic si es muy nuevo ya devuelve milisengundos """
        try:
            res = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        except Exception:
            raise
            res = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        
        return res

    """ Sample data
    0  domain:		data99.com.ar
    1  registrant:	20264536538
    2  registrar:	nicar
    3  registered:	2010-04-12 00:00:00
    4  changed:	2020-03-24 08:26:01.899786
    5  expire:		2021-04-12 00:00:00
    6
    7  contact:	20264536538
    8  name:		VAZQUEZ FLEXES ANDRES
    9  registrar:	nicar
    10 created:	2013-08-20 00:00:00
    11 changed:	2020-05-04 19:34:57.928489
    12
    13  nserver:	ns2.cluster311.com ()
    13b nserver:	ns1.cluster311.com ()
    14 registrar:	nicar
    15 created:	2016-06-30 23:14:21.131083
    """