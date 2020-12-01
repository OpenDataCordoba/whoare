"""
Iterate over priority domains and send data to server
"""
import argparse
from datetime import date, timedelta
import logging
from time import sleep
import requests
import sys
from whoare.zone_parsers.ar.news import NewDomains


logger = logging.getLogger(__name__)


class WhoAreNews:
    def __init__(self, push_url, token):
        self.push_url = push_url  # destination URL to share news
        self.token = token
        
        self.total_analizados = 0
        self.nuevos = 0
        self.ya_existian = 0
    
    def run(self, days_ago=3):
        nd = NewDomains()

        fromd = date.today() - timedelta(days=days_ago)
        dominios = nd.get_from_date_range(from_date=fromd)

        for dominio in dominios:
            logger.info(f' {self.nuevos}+{self.ya_existian}={self.total_analizados}/{len(dominios)} Before push {dominio}')
            response = nd.push_domain(dominio, self.push_url, self.token)    
            
            self.total_analizados += 1
            jresponse = response.json()
            if response.status_code == 400:
                self.ya_existian += 1
            elif response.status_code in [200, 201]:
                pdid = jresponse.get('id', 0)
                if pdid == 0:
                    self.ya_existian += 1
                else:
                    self.nuevos += 1
            
            logger.info(f' - Response {jresponse}')
        

def main():

    push_url = 'https://nic.opendatacordoba.org/api/v1/dominios/predominio/'
    
    parser = argparse.ArgumentParser(prog='whoare-news')
    parser.add_argument('--push_url', nargs='?', help='URL to post results to', type=str, default=push_url)
    parser.add_argument('--token', nargs='?', help='Token to use as Header Autorization', type=str, required=True)
    parser.add_argument('--days_ago', nargs='?', help='Days ago to read', type=int, default=3)
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

    was = WhoAreNews(push_url=args.push_url, token=args.token)

    was.run(days_ago=args.days_ago)