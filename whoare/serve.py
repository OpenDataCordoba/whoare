"""
Iterate over priority domains and send data to server
"""
import argparse
import logging
from time import sleep
import requests
from whoare.whoare import WhoAre
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
            print(domain)
            raise
            wa = WhoAre()
            raw = wa.get_raw(domain)
            self.post_one(raw)

            # if torify start a second queue
            if self.torify:
                domain = self.get_one()
                logger.info(f'Domain {domain} torify')
                wa = WhoAre()
                raw = wa.get_raw(domain, torify=True)
                self.post_one(raw)
            
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
    
    def post_one(self, raw):
        logger.info('POST one')
        headers = {'Authorization': f'Token {self.token}'}
        data = {'raw': raw}
        response = requests.post(self.post_url, data=data, headers=headers)
        jresponse = response.json()
        logger.info(f' - POST {jresponse}')
        return jresponse['ok']

def main():
    parser = argparse.ArgumentParser(prog='whoare-share')
    parser.add_argument('--get', nargs='?', help='URL to get domains from', type=str, default='https://nic.opendatacordoba.org/api/v1/dominios/next-priority/')
    parser.add_argument('--post', nargs='?', help='URL to post results to', type=str, required=True)
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