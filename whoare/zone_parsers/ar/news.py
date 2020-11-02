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

    def get_from_date_range(self, 
                            from_date=date.today() - timedelta(days=400),
                            to_date=date.today()):
        """ download and process last ~year """
        dia = from_date
        full_results = {}

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
                raise

            logger.error(f"===============\n{dia.strftime('%d-%m-%Y')} {c} {errors}")
        
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

        for zona, lista in full_results.items():
            f = open(f'{zona}.txt', 'w')
            for dom in lista:
                f.write(f'{dom}\n')
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
            try:
                self.session.get(f'{self.base_domain}/{self.home}')
                # call via ajax the required date
                internal_ajax_url = f'{self.base_domain}/edicion/actualizar/{date}'
                self.session.get(internal_ajax_url)
                home2_response = self.session.get(f'{self.base_domain}/{self.home}')
            except:
                logger.error('Error GET from BOE')
                return {'zonas': {}, 'errors': {}}
                
            if f"var fechaSeleccionada = '{date}';" not in home2_response.text:
                logger.error('Expected JS not foud')
                return {'zonas': {}, 'errors': {}}

            ret = self.download_pdf(date=date, path=final_pdf)
            if ret is None:
                return {'zonas': {}, 'errors': {}}
        
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
        try:
            data = response.json()
        except:
            logger.error(f'INVALID JSON for {date} {path}')
            return None
        b64 = data['pdfBase64']
        bin_pdf = base64.b64decode(b64)
        f = open(path, 'wb')
        f.write(bin_pdf)
        f.close()
        return True

    def read_pdf(self, pdf_path):
        # Read pdf into list of DataFrame
        df = tabula.read_pdf(pdf_path, pages='all')
        valid_zones = WhoAr.zones()

        results = {'zonas': {}, 'errors': {}}
        last_dominio = ''
        last_zona = ''
        zona = ''
        valid_zone = False
        file_name = pdf_path.split('/')[-1]
        last_error_code = file_name
        c = 0
        last_df = None
        last_any_df = None
        
        for dom in df:
            c += 1
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
                        if last_dominio > url and last_dominio[0] != url[0]:
                            if last_zona != zona:
                                logger.info(f'Changed zone OK {zona} at {dom_name}.{zona}')
                                last_zona = zona
                                valid_zone = True
                            else:
                                ix = '' if last_df is None else last_df.index
                                cl = '' if last_df is None else last_df.columns
                                ix2 = '' if last_any_df is None else last_df.index
                                cl2 = '' if last_any_df is None else last_df.columns
                                v2 = '[]' if last_any_df is None else last_df.values
                                logger.error(f'Changed ZONE expected! \n\t{ix}\n\t{cl}\n\t{ix2}\n\t{cl2}\n\t{v2}\n\t{dom.index}\n\t{dom.columns}')
                                logger.error(f'Changed to {dom_name}.{zona}')
                                # skip all not-sure domains
                                valid_zone = False
                                last_error_code = f'error-{c}-{zona}-{file_name}'
                        
                        if valid_zone:
                            if zona not in results['zonas']:
                                results['zonas'][zona] = []
                            results['zonas'][zona].append(url)
                        else:
                            if last_error_code not in results['errors']:
                                results['errors'][last_error_code] = []
                            results['errors'][last_error_code].append(url)
                        
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
                if new_zone == 'net.a': new_zone = 'net.ar' # (?)
                if new_zone == 'org.a': new_zone = 'org.ar' # (?)
                if new_zone == 'gob.a': new_zone = 'gob.ar' # (?)
                if new_zone == 'tur.a': new_zone = 'gob.ar' # (?)
                if new_zone == 'a': new_zone = 'ar' # (?)
                
                if new_zone not in valid_zones:
                    logger.error(f'BAD ZONE {new_zone}')
                else:
                    zona = new_zone
                    logger.info(f'Zona FOUND: {zona} at {dom.columns}\n\t{dom.index}')

                last_df = dom

        return results
