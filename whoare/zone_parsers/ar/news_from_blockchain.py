import csv
from datetime import timedelta, date
import logging
import os
import re
import requests
from time import sleep

from whoare.zone_parsers.ar.who import WhoAr
logger = logging.getLogger(__name__)


class NewDomains:
    """ leer los CSVs que se publican en blockchain
        https://rdlist.nic.ar/rd_list/
    """
    def __init__(self, ua="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"):
        self.base_domain = 'https://rdlist.nic.ar/rd_list/download'
        self.ua = ua
        self.data_path = 'whoare/zone_parsers/ar/data'

    def get_from_date_range(self, 
                            from_date=date.today() - timedelta(days=3),
                            to_date=date.today(),
                            push_url=None,
                            api_key=None):
        """ download and process last ~year 
            If push_url and api_key exists we send push domains"""

        dia = from_date
        full_results = {}

        c = 0
        errors = 0
        while dia < to_date:
            dia += timedelta(days=1)
            
            logger.info(f'Downloading {dia}')
            try:
                results = self.get_from_date(dated=dia)
            except Exception as e:
                logger.error(f'Error on date {dia}: {e}')
                raise

            logger.info(f"===============\n{dia} {c} {errors}")
        
            # grabar cada lista de errores en un archivo
            for code, lista in results['errors'].items():
                f = open(f'{code}.txt', 'w')
                for dom in lista:
                    f.write(f'{dom}\n')
                f.close()

            # eliminar duplicados
            for zona, lista in results['zonas'].items():
                if zona not in full_results:
                    full_results[zona] = []
                for dom in lista:
                    if dom not in full_results[zona]:
                        full_results[zona].append(dom)

        final = []
        for zona, lista in full_results.items():
            f = open(f'{zona}.txt', 'w')
            for dom in lista:
                f.write(f'{dom}\n')
                final.append(dom)
            f.close()

        return final

    def push_domain(self, domain, push_url, api_key):
        """ push domain to external server """

        headers = {'Authorization': f'Token {api_key}'}
        data = {'dominio': domain}
        logger.info(f'Push new domain {domain} to {push_url}')
        response = requests.post(url=push_url, data=data, headers=headers)
        jresponse = response.json()
        logger.info(f' - Response [{response.status_code}]: {jresponse}')
        return response
        
    def date_to_csvid(self, dated):
        """ los CSVs estan enumerados. Cada fecha es un numero
            1022 = 2020-12-15 

            del 303 pasa al 316 (?) 
            del 203 pasa al 312 y despues sigue con 204 (?) 
            
            NO SIRVE """

        # base = date(2020, 12, 25)
        # daydiff = (dated - base).days
        # return 1022 + daydiff

        # usar el filtro por fecha
        filter_url = f'https://rdlist.nic.ar/rd_list/?date_filter={dated.strftime("%d-%m-%Y")}'
        response = requests.get(filter_url)

        rgx = re.search(r'/rd_list/download/(?P<csvid>[0-9]+)/csv/', response.text)
        if rgx is not None:
            return rgx.group('csvid')
        
        logger.error(f'CSVID not found for {dated}')
        return None

    def get_from_date(self, dated):
        """ Download specific date PDF and process it.
            sample date: 08-10-2019 DD-MM-YYYY
            """
        # check if exists
        final_csv = os.path.join(self.data_path, f'{dated.strftime("%Y-%m-%d")}-blockchain.csv')

        if not os.path.isfile(final_csv):
                
            ret = self.download_csv(dated=dated, path=final_csv)
            if ret is None:
                return {'zonas': {}, 'errors': {}}
        
        else:
            logger.info(f'Skip download. File already exists {dated} {final_csv}')
        
        results = self.read_csv(csv_path=final_csv)
        return results
        
    def download_csv(self, dated, path):
        """ descargar el PDF "actual" (la pagina guarda en sesion o algo similar el dia elegido) """

        if os.path.isfile(path):
            logger.info(f'Skip download. File already exists {dated} {path}')
            return True

        headers = {"User-Agent": self.ua}
        csvid = self.date_to_csvid(dated)
        if csvid is None:
            # el 29/3/2019 por ejemplo no existe (?)
            return None

        url = f'{self.base_domain}/{csvid}/csv'
        try:
            response = requests.get(url, headers=headers)
        except:
            logger.error('Error GET from blockchain CSV')
            return None

        if response.status_code >= 400 or response.content is None or response.text == '':
            logger.error(f'Error getting {url} from blockchain CSV {response.status_code}')
            return None
    
        f = open(path, 'wb')
        f.write(response.content)
        f.close()

        logger.info(f'SAVED {url} to {path}')
        return True

    def read_csv(self, csv_path):
        logger.info(f'Reading CSV {csv_path}')
        results = {'zonas': {}, 'errors': {}}

        if not os.path.isfile(csv_path):
            return results
                
        f = open(csv_path)
        reader = csv.DictReader(f)
        # tipo	dominio	zona	id_dominio	titular	numero_doc	tipo_doc	fecha_registro
        # tipo = A (alta) T (transferencia)

        for row in reader:

            zona = row['zona']
            dominio = row['dominio']  # no incluye la zona
            if zona not in results['zonas']:
                results['zonas'][zona] = []
            
            # revisar dominios con catacteres espciales
            idna_dominio = dominio.encode().decode('idna')
            if dominio != idna_dominio:
                logger.info(f'Corrigiendo dominio con catacteres especiales {dominio} != {idna_dominio}')
                dominio = idna_dominio

            url = f'{dominio}.{zona}'
            results['zonas'][zona].append(url)
            logger.info(f'DOMAIN FOUND {url}')
        
        return results
