[![Travis (.org)](https://img.shields.io/travis/avdata99/whoare?style=for-the-badge)](https://travis-ci.org/github/avdata99/whoare)
[![GitHub All Releases](https://img.shields.io/github/downloads/avdata99/whoare/total?style=for-the-badge)](https://github.com/avdata99/whoare/releases)
[![GitHub Issues](https://img.shields.io/github/issues/avdata99/whoare?style=for-the-badge)](https://github.com/avdata99/whoare/issues)
[![GitHub PR](https://img.shields.io/github/issues-pr/avdata99/whoare?style=for-the-badge)](https://github.com/avdata99/whoare/pulls)
[![Licence](https://img.shields.io/github/license/avdata99/whoare?style=for-the-badge)](https://github.com/avdata99/whoare/blob/main/LICENSE)
[![Pypi py version](https://img.shields.io/pypi/pyversions/sss-beneficiarios-hospitales?style=for-the-badge)](https://pypi.org/project/sss-beneficiarios-hospitales/)
[![Last Commit](https://img.shields.io/github/last-commit/avdata99/whoare?style=for-the-badge)](https://github.com/avdata99/whoare/commits/main)

# A WhoIs parser

```python
from whoare.whoare import WhoAre
wa = WhoAre()
wa.load('argentina.ar')

str(wa.domain)
'Domain argentina at ar. Registered at 2016-11-08 09:26:59.345164'

str(wa.registrant)
'Registrant nic.ar UIF 99999999994'

str(wa.dnss[0])
'DNS ns1.afip.gob.ar'
str(wa.dnss[1])
'DNS ns2.afip.gob.ar'

```