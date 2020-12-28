![Lint and test](https://github.com/avdata99/whoare/workflows/Lint%20and%20test/badge.svg?branch=main)
[![GitHub All Releases](https://img.shields.io/github/downloads/avdata99/whoare/total?style=for-the-badge)](https://github.com/avdata99/whoare/releases)
[![GitHub Issues](https://img.shields.io/github/issues/avdata99/whoare?style=for-the-badge)](https://github.com/avdata99/whoare/issues)
[![GitHub PR](https://img.shields.io/github/issues-pr/avdata99/whoare?style=for-the-badge)](https://github.com/avdata99/whoare/pulls)
[![Licence](https://img.shields.io/github/license/avdata99/whoare?style=for-the-badge)](https://github.com/avdata99/whoare/blob/main/LICENSE)
[![Pypi py version](https://img.shields.io/pypi/pyversions/whoare?style=for-the-badge)](https://pypi.org/project/whoare/)
[![Last Commit](https://img.shields.io/github/last-commit/avdata99/whoare?style=for-the-badge)](https://github.com/avdata99/whoare/commits/main)

# A WhoIs parser

Just a `whois` parser

Available countries:
 - `.ar`: Argentina

## Sample

```python
from whoare.whoare import WhoAre
wa = WhoAre()
wa.load('fernet.com.ar')  # optional torify=True to run "torify whois ..."

wa.domain.base_name
'fernet'
wa.domain.zone
'com.ar'
wa.domain.full_name()
'fernet.com.ar'
wa.domain.registered
datetime.datetime(2020, 5, 7, 10, 44, 4, 210977)
wa.domain.expire
datetime.datetime(2021, 5, 7, 0, 0)

wa.registrant.name
'XXXX jose XXXXX'
wa.registrant.legal_uid
'20XXXXXXXX9'
wa.dnss[0].name
'ns2.sedoparking.com'
wa.dnss[1].name
'ns1.sedoparking.com'
```

## Get new domains

### Argentina

```python
from datetime import date
from whoare.zone_parsers.ar.news_from_blockchain import NewDomains
nd = NewDomains()
nd.data_path = ''  # here
results = nd.get_from_date(date(2020, 3, 28))

{
    'zonas': {
        'com.ar': [
            '3cconstrucciones.com.ar',
            '4kids.com.ar'
            ],
        'ar': [
            'andamios.ar',
            'apuesta.ar',
            'camaras.ar'
            ],
        'tur.ar': [
            'villacarlospaz.tur.ar'
            ]
        },
    'errors': {}
}

```
