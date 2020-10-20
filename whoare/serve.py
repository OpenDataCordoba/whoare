"""
Iterate over priority domains and send data to server
"""
import logging
from time import sleep
import requests
from whoare.whoare import WhoAre
logger = logging.getLogger(__name__)


class WhoAreShare:
    def __init__(self, get_domains_url, post_url, token, torify=True, pause_between_calls=20):
        self.torify = torify  # use local IP and also torify
        self.post_url = post_url  # destination URL to share data (will be processed outside)
        self.token = token
        self.get_domains_url = get_domains_url  # URL to get domains from
        self.pause_between_calls = pause_between_calls

    def run(self):
        """ get domains and _whois_ them """
        while True:
            domain = self.get_one()
            wa = WhoAre()
            raw = wa.get_raw(domain)
            self.post_one(raw)

            # if torify start a second queue
            if self.torify:
                domain = self.get_one()
                wa = WhoAre()
                raw = wa.get_raw(domain, torify=True)
                self.post_one(raw)
            
            sleep(self.pause_between_calls)
                
    def get_one(self):
        logger.info('Getting one')
        headers = {'Authorization': f'Token {self.token}'}
        response = requests.get(self.get_domains_url, headers=headers)
        jresponse = response.json()
        logger.info(f' - Get {jresponse}')
        return jresponse['domain']
    
    def post_one(self, raw):
        logger.info('POST one')
        headers = {'Authorization': f'Token {self.token}'}
        data = {'raw': raw}
        response = requests.post(self.post_url, data=data headers=headers)
        jresponse = response.json()
        logger.info(f' - POST {jresponse}')
        return jresponse['ok']
    