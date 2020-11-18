"""
Iterate over priority domains and send data to server
"""
import argparse
from datetime import datetime
import json
import logging
from time import sleep
import requests
import sys
from whoare.whoare import WhoAre
from whoare import __version__

logger = logging.getLogger(__name__)


class WhoAreShare:
    def __init__(self, get_domains_url, post_url, token, torify=True, pause_between_calls=41, from_path=None):
        self.torify = torify  # use local IP and also torify
        self.post_url = post_url  # destination URL to share data (will be processed outside)
        self.token = token
        self.get_domains_url = get_domains_url  # URL to get domains from
        self.pause_between_calls = pause_between_calls
        self.from_path = from_path

        self.total_analizados = 0
        self.sin_cambios = 0
        self.caidos = 0
        self.nuevos = 0
        self.renovados = 0
        self.otros_cambios = 0
        self.errores = 0

        self.processed = []  # skip duplicates

    def run(self):
        """ get domains and _whois_ them """
        if self.from_path is not None:
            self.run_from_path(self.from_path)
        else:
            self.run_from_priority()

    def run_from_priority(self):
        """ get priority domains from API """
        logger.info('Start runing from priority')
        while True:
            
            domain = self.get_one()
            self.load_one(domain, torify=False)

            sleep(self.pause_between_calls / 2)
            # if torify start a second queue
            if self.torify:
                domain = self.get_one()
                self.load_one(domain, torify=True)
            
            sleep(self.pause_between_calls / 2)
    
    def run_from_path(self, path):
        """ open a file and update those domains """
        f = open(path)
        domain_data = f.read()
        f.close()

        domain_list = domain_data.split('\n')

        c = 0
        while True:
            
            domain = domain_list[c]
            self.load_one(domain, torify=False)

            sleep(self.pause_between_calls / 2)
            if self.torify:
                c += 1
                if c >= len(domain_list): break
                domain = domain_list[c]
                self.load_one(domain, torify=True)
            
            sleep(self.pause_between_calls / 2)
            c += 1
            if c >= len(domain_list): break

    def load_one(self, domain, torify):
        """ analyze and push one domain """
        logger.info(f'Domain {domain} tor:{torify}')

        if domain in self.processed:
            logger.error(f'Duplicated domain {domain}. Skipping')
            return
        self.processed.append(domain)

        wa = WhoAre()
        try:
            wa.load(domain, torify=torify)
        except Exception as e:
            logger.error(f'Whois ERROR {e}')
            self.errores += 1
        else:
            self.post_one(wa)

    def get_one(self):
        """ get the next priority from API """
        logger.debug('Getting one')
        headers = {'Authorization': f'Token {self.token}'}
        # if I ask 2, I get the same (?)
        # didn't worked data = {'order': str(self.total_analizados)}
        data = {'t': datetime.now().timestamp()}
        response = requests.get(self.get_domains_url, data=data, headers=headers)
        if response.status_code != 200:
            raise ValueError(f'Error GET status {response.status_code}: {response.text}')
        
        try:
            jresponse = response.json()
        except Exception:
            print(f'ERROR parsing {response.text}')
            raise
        
        dom = jresponse['results'][0]
        logger.info(f" - Got {dom['domain']} {dom.get('estado', '')} readed {dom.get('data_readed', '')} expire {dom.get('expire', '')} priority {dom.get('priority_to_update', '-')}")

        return dom['domain']
    
    def post_one(self, wa):
        """ post results to server """
        headers = {'Authorization': f'Token {self.token}'}
        data = wa.as_dict()
        data['whoare_version'] = __version__
        logger.debug(f'POSTing {data}')
        str_data = json.dumps(data)
        final = {'domain': str_data}
        response = requests.post(self.post_url, data=final, headers=headers)
        jresponse = response.json()
        logger.debug(f' - POST {jresponse}')
        self.analyze_changes(jresponse)
        return jresponse['ok']
    
    def analyze_changes(self, response):
        if not response['ok']:
            self.errores += 1
            return
            
        cambios = response.get('cambios', [])   
        if cambios == []:
            if response.get('created', False):
                self.nuevos += 1
            else:
                self.sin_cambios += 1  
        elif 'estado' in [c['campo'] for c in cambios]:
            for cambio in cambios:
                if cambio['campo'] == 'estado':
                    if cambio['anterior'] == 'disponible':
                        self.nuevos += 1
                    elif cambio['anterior'] == 'no disponible':
                        self.caidos += 1
        elif 'dominio_expire' in [c['campo'] for c in cambios]:
            self.renovados += 1
        else:
            self.otros_cambios += 1

        self.total_analizados += 1
        
        logger.info(f'STATUS [{self.total_analizados}]{self.errores} renovados:{self.renovados} caidos:{self.caidos} sin cambios:{self.sin_cambios} nuevos:{self.nuevos} otros:{self.otros_cambios}')


def main():

    # base_domain = 'http://localhost:8000'
    base_domain = 'https://nic.opendatacordoba.org'
    default_get = f'{base_domain}/api/v1/dominios/next-priority/'
    default_post = f'{base_domain}/api/v1/dominios/dominio/update_from_whoare/'
    
    parser = argparse.ArgumentParser(prog='whoare-share')
    parser.add_argument('--get', nargs='?', help='URL to get domains from', type=str, default=default_get)
    parser.add_argument('--post', nargs='?', help='URL to post results to', type=str, default=default_post)
    parser.add_argument('--token', nargs='?', help='Token to use as Header Autorization', type=str, required=True)
    parser.add_argument('--torify', nargs='?', type=bool, default=True, help='Use torify for WhoIs command')
    parser.add_argument('--pause', nargs='?', help='Pause between calls', default=41, type=int)
    parser.add_argument('--from_path', nargs='?', help='If not used we will get priorities from API. This is usted for new-domain lists', type=str)
    parser.add_argument('--log_level', nargs='?', default='INFO', type=str)
    
    args = parser.parse_args()

    if args.log_level == 'INFO':
        log_level = logging.INFO
    elif args.log_level == 'DEBUG':
        log_level = logging.DEBUG
    
    logger.setLevel(log_level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    was = WhoAreShare(
        get_domains_url=args.get,
        post_url=args.post,
        token=args.token,
        torify=args.torify,
        pause_between_calls=args.pause,
        from_path=args.from_path
    )

    was.run()