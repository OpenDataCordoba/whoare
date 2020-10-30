[![Travis (.org)](https://img.shields.io/travis/avdata99/whoare?style=for-the-badge)](https://travis-ci.org/github/avdata99/whoare)
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
from whoare.zone_parsers.ar.news import NewDomains
nd = NewDomains()
nd.data_path = ''  # here
results = nd.get_from_date('03-12-2019')

print(results[10])
{'url': '3devo.ar', 'error': None, 'dominio_base': '3devo', 'zona': 'ar'}
print(results[1000])
{'url': 'pinturasacasa.ar', 'error': None, 'dominio_base': 'pinturasacasa', 'zona': 'ar'}
print(results[1500])
{'url': 'ofamachines.org.ar', 'error': None, 'dominio_base': 'ofamachines', 'zona': 'org.ar'}

```
