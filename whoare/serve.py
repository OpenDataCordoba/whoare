"""
Iterate over priority domains and send data to server
"""
import argparse
import json
import logging
from time import sleep
import requests
import sys
from whoare.whoare import WhoAre
from whoare import __version__

logger = logging.getLogger(__name__)


class WhoAreShare:
    def __init__(self, get_domains_url, post_url, token, torify=True, pause_between_calls=41):
        self.torify = torify  # use local IP and also torify
        self.post_url = post_url  # destination URL to share data (will be processed outside)
        self.token = token
        self.get_domains_url = get_domains_url  # URL to get domains from
        self.pause_between_calls = pause_between_calls

    def run(self):
        """ get domains and _whois_ them """
        logger.info('Start runing')
        while True:
            
            domain = self.get_one()
            logger.info(f'Domain {domain}')

            wa = WhoAre()
            try:
                wa.load(domain)
            except:
                pass
            else:
                self.post_one(wa)

            # if torify start a second queue
            if self.torify:
                domain = self.get_one()
                logger.info(f'Domain {domain} torify')
                wa = WhoAre()
                try:
                    wa.load(domain, torify=True)
                except:
                    pass
                else:
                    self.post_one(wa)

            sleep(self.pause_between_calls)
                            
    def get_one(self):
        logger.info('Getting one')
        headers = {'Authorization': f'Token {self.token}'}
        response = requests.get(self.get_domains_url, headers=headers)
        if response.status_code != 200:
            raise ValueError(f'Error GET status {response.status_code}: {response.text}')
        
        try:
            jresponse = response.json()
        except Exception:
            print(f'ERROR parsing {response.text}')
            raise
        
        logger.info(f' - Get {jresponse}')
        
        return jresponse[0]['domain']
    
    def post_one(self, wa):
        logger.info(f'POST {wa}')
        headers = {'Authorization': f'Token {self.token}'}
        data = wa.as_dict()
        data['whoare_version'] = __version__
        logger.info(f'POSTing {data}')
        str_data = json.dumps(data)
        final = {'domain': str_data}
        response = requests.post(self.post_url, data=final, headers=headers)
        jresponse = response.json()
        logger.info(f' - POST {jresponse}')
        return jresponse['ok']

def main():
        
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

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
    
    args = parser.parse_args()

    was = WhoAreShare(
        get_domains_url=args.get,
        post_url=args.post,
        token=args.token,
        torify=args.torify,
        pause_between_calls=args.pause
    )

    was.run()