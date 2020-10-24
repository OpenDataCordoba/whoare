import pytz
from datetime import datetime
import logging
from whoare.exceptions import (TooManyQueriesError, ServiceUnavailableError, 
                               UnknownError, UnexpectedParseError,
                               UnexpectedDomainError)


logger = logging.getLogger(__name__)
tz = pytz.timezone('America/Argentina/Cordoba')


class WhoAr:

    @classmethod
    def zones(cls):
        return ['ar', 'com.ar', 'gob.ar', 'gov.ar', 'int.ar', 'mil.ar', 'org.ar', 'tur.ar', 'net.ar']

    def is_free(self, raw):
        """ determine if domain is free """
        return "El dominio no se encuentra registrado" in raw

    def check_errors(self, raw):
        
        if "el servicio WHOIS de NIC Argentina se encuentra inactivo" in raw:
            raise ServiceUnavailableError()

        if "Excediste la cantidad permitida de consultas" in raw:
            raise TooManyQueriesError()

        if "fgets: Conexión reinicializada por la máquina remota" in raw:
            raise UnknownError()
        

    def parse(self, raw, parent):
        from whoare.base import Registrant, DNS
        logger.debug(f'Parsing {raw}')
        lines = raw.split('\n')

        real_lines = []
        for line in lines:
            if line.startswith('%') or line == '':
                continue
            real_lines.append(line)

        logger.debug(f'Parsing cleaned {real_lines}')
        
        # ==========================================
        field, value = self._parse_line(real_lines[0])
        if field != 'domain':
            raise UnexpectedParseError(f'Field {field} is not "domain"')
        
        fullname = parent.domain.full_name()
        if value != fullname:
            # take care of IDNA domains https://github.com/avdata99/whoare/issues/1
            # xn--caaconruda-u9a.ar != cañaconruda.ar
            idna_ver = fullname.encode('idna').decode('utf8')
            if value != idna_ver:
                raise UnexpectedDomainError(f'Unexpected domain {value} != {parent.domain.full_name()} ({idna_ver})')
        
        # ==========================================
        field, value = self._parse_line(real_lines[1])
        if field != 'registrant':
            raise UnexpectedParseError(f'Field {field} is not "registrant"')
        
        registrant_uid = value

        # ignore line 2, registrar

        # ==========================================
        field, value = self._parse_line(real_lines[3])
        if field != 'registered':
            raise UnexpectedParseError(f'Field {field} is not "registered"')
        
        parent.domain.registered = self._get_nic_date(value)
        
        # ==========================================
        field, value = self._parse_line(real_lines[4])
        if field != 'changed':
            raise UnexpectedParseError(f'Field {field} is not "changed"')

        parent.domain.changed = self._get_nic_date(value)
        
        # ==========================================
        field, value = self._parse_line(real_lines[5])
        if field != 'expire':
            raise UnexpectedParseError(f'Field {field} is not "expire"')

        parent.domain.expire = self._get_nic_date(value)
        
        # ==========================================
        field, value = self._parse_line(real_lines[6])
        if field != 'contact':
            raise UnexpectedParseError(f'Field {field} is not "contact"')

        if value != registrant_uid:
            raise UnexpectedParseError(f'Legal UID diff {value} != {registrant_uid}')

        # ==========================================
        field, value = self._parse_line(real_lines[7])
        if field != 'name':
            raise UnexpectedParseError(f'Field {field} is not "name"')

        parent.registrant = Registrant(name=value, legal_uid=registrant_uid)

        # ignore line, registrar

        # ==========================================
        field, value = self._parse_line(real_lines[9])
        if field != 'created':
            raise UnexpectedParseError(f'Field {field} is not "created"')
        
        parent.registrant.created = self._get_nic_date(value)

        # ==========================================
        field, value = self._parse_line(real_lines[10])
        if field != 'changed':
            raise UnexpectedParseError(f'Field {field} is not "changed"')
        
        parent.registrant.changed = self._get_nic_date(value)

        if len(real_lines) > 11:
            # ==========================================
            field, value = self._parse_line(real_lines[11])
            n = 11
            while field == "nserver":
                parts = value.split()
                ns = parts[0]
                logger.info(f'DNS found {ns}')
                parent.dnss.append(DNS(name=ns))
                n += 1
                if len(real_lines) > n:
                    field, value = self._parse_line(real_lines[n])
                else:
                    field = None
        
    def _parse_line(self, line):
        parts = line.split(':')
        field = parts[0].lower().strip()
        value = ':'.join(parts[1:]).lower().strip()

        return field, value

    def _get_nic_date(self, date_str):
        """ nic si es muy nuevo ya devuelve milisengundos """
        
        try:
            res = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            res = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

        res = tz.localize(res, is_dst=True)        
        # logger.debug(f'_get_nic_date {date_str} {res}')
        return res
