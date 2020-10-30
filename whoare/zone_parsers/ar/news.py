""" get new domains """
import base64
from datetime import timedelta, date
import logging
import numpy as np
import os
import requests
import tabula
from time import sleep

from whoare.zone_parsers.ar.who import WhoAr
logger = logging.getLogger(__name__)


class NewDomains:
    def __init__(self, ua="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"):
        self.base_domain = 'https://www.boletinoficial.gob.ar'
        self.home = 'seccion/cuarta'
        self.session = requests.Session()
        self.ua = ua
        self.data_path = 'whoare/zone_parsers/ar/data'

    def get_from_date_range(self, from_date=date.today() - timedelta(days=400), to_date=date.today()):
        """ download and process last ~year """
        dia = from_date
        full_results = []

        c = 0
        errors = 0
        while dia < to_date:
            dia += timedelta(days=1)
            if dia.weekday() in [6, 7]:
                # skip weekends
                continue
            
            logger.info(f'Downloading {dia}')
            try:
                results = self.get_from_date(date=dia.strftime('%d-%m-%Y'))
            except Exception as e:
                logger.error(f'Error on date {dia}: {e}')
                continue

            for result in results:
                if result['error'] is None:
                    if result['url'] not in full_results:
                        c += 1
                        full_results.append(result['url'])
                else:
                    errors += 1
                logger.error(f"===============\n{dia.strftime('%d-%m-%Y')} {c} {errors} At {result['url']}\n===============")
        
        f = open('tmp.txt', 'w')
        for r in full_results:
            f.write(r)
        f.close()
        return full_results
        
    def get_from_date(self, date):
        """ Download specific date PDF and process it.
            sample date: 08-10-2019 DD-MM-YYYY
            """
        # check if exists
        final_pdf = os.path.join(self.data_path, f'{date}.pdf')

        if not os.path.isfile(final_pdf):
            
            # go inside home
            self.session.headers.update({"User-Agent": self.ua})
            self.session.get(f'{self.base_domain}/{self.home}')
            # call via ajax the required date
            internal_ajax_url = f'{self.base_domain}/edicion/actualizar/{date}'
            self.session.get(internal_ajax_url)
            home2_response = self.session.get(f'{self.base_domain}/{self.home}')
            
            if f"var fechaSeleccionada = '{date}';" not in home2_response.text:
                return False, 'Expected JS not foud'

            self.download_pdf(date=date, path=final_pdf)
        
        else:
            logger.info(f'Skip download. File already exists {date} {final_pdf}')
        
        results = self.read_pdf(pdf_path=final_pdf)
        return results
        
    def download_pdf(self, date, path):
        """ descargar el PDF "actual" (la pagina guarda en sesion o algo similar el dia elegido) """

        if os.path.isfile(path):
            logger.info(f'Skip download. File already exists {date} {path}')
            return

        response = self.session.post(f'{self.base_domain}/pdf/download_section', data={'nombreSeccion': 'cuarta'})
        data = response.json()
        b64 = data['pdfBase64']
        bin_pdf = base64.b64decode(b64)
        f = open(path, 'wb')
        f.write(bin_pdf)
        f.close()

    def read_pdf(self, pdf_path):
        # Read pdf into list of DataFrame
        df = tabula.read_pdf(pdf_path, pages='all')
        valid_zones = WhoAr.zones()

        results = []
        last_dominio = ''
        last_zona = ''
        zona = ''
        
        for dom in df:                                
            if len(dom.values) > 0:
                for dominio in dom.values:
                    if type(dominio[0]) == float:
                        if len(dominio) == 1 or type(dominio[1]) == float:
                            # logger.error(f'Bad line! \n\t{dom.index}\n\t{dom.columns}\n\t{dom.values}')
                            continue  # (?)
                        else:
                            dom_name = dominio[1]
                    else:
                        dom_name = dominio[0]

                    if dom_name != '' and dom_name == dom_name.lower() and ' ' not in dom_name and str(dom_name) != 'nan' and zona != '':
                        url = f"{dom_name}.{zona}"
                        error = None
                        if last_dominio > url and last_dominio[0] != url[0]:
                            if last_zona != zona:
                                logger.info(f'Changed zone OK {zona} at {dom_name}.{zona}')
                                last_zona = zona
                            else:
                                logger.error(f'Changed ZONE expected! \n\t{last_df.index}\n\t{last_df.columns}\n\t{last_any_df.index}\n\t{last_any_df.columns}\n\t{last_any_df.values}\n\t{dom.index}\n\t{dom.columns}')
                                error = f'Expected zone to change {dom_name}.{zona}'
                                logger.error(f'Changed to {dom_name}.{zona}')
                                
                        results.append({'url': url, 'error': error, 'dominio_base': dom_name, 'zona': zona})
                        last_dominio = url
                    # else:
                    #     logger.error(f'Bad line2! \n\t{dom.index}\n\t{dom.columns}\n\t{dom.values}')
                        
            skip = ['Unnamed', 'Boletín Oficial', 'NOMBRE DEL DOMINIO', 'Transferencias', 'Altas']
            ok = True
            for s in skip:
                if s in dom.columns[0]:
                    ok = False
                    logger.debug(f'SKIP ZONE {dom.columns[0]}')
            
            last_any_df = dom

            if ok:
                new_zone = dom.columns[0]
                if new_zone == 'com.a': new_zone = 'com.ar' # (?)
                
                if new_zone not in valid_zones:
                    logger.error(f'BAD ZONE {new_zone}')
                else:
                    zona = new_zone
                    logger.info(f'Zona FOUND: {zona} at {dom.columns}\n\t{dom.index}')

                last_df = dom

        return results
