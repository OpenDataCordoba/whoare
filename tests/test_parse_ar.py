from datetime import datetime
import mock
import pytz
from whoare.whoare import WhoAre

tz = pytz.timezone('America/Argentina/Cordoba')


def whois_from_txt(path):
    f = open(path)
    content = f.read()
    f.close()
    
    process_mock = mock.Mock()
    attrs = {
        'communicate.return_value': [content.encode()],
        'returncode': 0
        }
    process_mock.configure_mock(**attrs)
    
    return process_mock


@mock.patch('subprocess.Popen')
def test_data99(mock_subproc_popen):

    wa = WhoAre()    
    mock_subproc_popen.return_value = whois_from_txt('whoare/zone_parsers/ar/sample_data99.txt')
    wa.load('data99.com.ar')
    assert mock_subproc_popen.called
    
    assert wa.domain.base_name == 'data99'
    assert wa.domain.zone == 'com.ar'
    assert not wa.domain.is_free
    assert wa.domain.registered == tz.localize(datetime(2010, 4, 12, 0, 0, 0), is_dst=True)
    assert wa.domain.changed == tz.localize(datetime(2020, 3, 24, 8, 26, 1, 899786), is_dst=True)
    assert wa.domain.expire == tz.localize(datetime(2021, 4, 12, 0, 0, 0), is_dst=True)
    
    assert wa.registrant.name == 'gomez pedro'
    assert wa.registrant.legal_uid == '20xxxxxxxx8'
    assert wa.registrant.created == tz.localize(datetime(2013, 8, 20, 0, 0, 0), is_dst=True)
    assert wa.registrant.changed == tz.localize(datetime(2020, 5, 4, 19, 34, 57, 928489), is_dst=True)
    
    assert wa.dnss[0].name == 'ns2.cluster311.com'
    assert wa.dnss[1].name == 'ns1.cluster311.com'

@mock.patch('subprocess.Popen')
def test_free_01(mock_subproc_popen):

    wa = WhoAre()    
    mock_subproc_popen.return_value = whois_from_txt('whoare/zone_parsers/ar/sample_free.txt')
    wa.load('domainfree.com.ar')
    assert mock_subproc_popen.called
    assert wa.domain.is_free

@mock.patch('subprocess.Popen')
def test_fernet(mock_subproc_popen):

    wa = WhoAre()    
    mock_subproc_popen.return_value = whois_from_txt('whoare/zone_parsers/ar/sample_fernet.txt')
    wa.load('fernet.com.ar')
    assert mock_subproc_popen.called
    
    assert wa.domain.base_name == 'fernet'
    assert wa.domain.zone == 'com.ar'
    assert not wa.domain.is_free
    assert wa.domain.registered == tz.localize(datetime(2020, 5, 7, 10, 44, 4, 210977), is_dst=True)
    assert wa.domain.changed == tz.localize(datetime(2020, 5, 7, 14, 34, 40, 828423), is_dst=True)
    assert wa.domain.expire == tz.localize(datetime(2021, 5, 7, 0, 0, 0), is_dst=True)

    assert wa.registrant.name == 'perez juan'
    assert wa.registrant.legal_uid == '20xxxxxxxx9'
    assert wa.registrant.created == tz.localize(datetime(2013, 8, 19, 0, 0, 0), is_dst=True)
    assert wa.registrant.changed == tz.localize(datetime(2020, 10, 11, 17, 37, 54, 831645), is_dst=True)
    
    assert wa.dnss[0].name == 'ns2.sedoparking.com'
    assert wa.dnss[1].name == 'ns1.sedoparking.com'


@mock.patch('subprocess.Popen')
def test_nic(mock_subproc_popen):

    wa = WhoAre()    
    mock_subproc_popen.return_value = whois_from_txt('whoare/zone_parsers/ar/sample_nic.txt')
    wa.load('nic.ar')
    assert mock_subproc_popen.called
    
    assert wa.domain.base_name == 'nic'
    assert wa.domain.zone == 'ar'
    assert not wa.domain.is_free
    assert wa.domain.registered == tz.localize(datetime(1998, 5, 29, 0, 0, 0), is_dst=True)
    assert wa.domain.changed == tz.localize(datetime(2019, 10, 7, 16, 23, 59, 503535), is_dst=True)
    assert wa.domain.expire == tz.localize(datetime(2020, 5, 1, 0, 0, 0), is_dst=True)

    assert wa.registrant.name == 'nic.ar'
    assert wa.registrant.legal_uid == '99999999994'
    assert wa.registrant.created == tz.localize(datetime(2016, 9, 26, 12, 4, 48, 869673), is_dst=True)
    assert wa.registrant.changed == tz.localize(datetime(2016, 9, 26, 17, 39, 38, 373610), is_dst=True)
    
    assert wa.dnss[0].name == 'ns5.rdns.ar'
    assert wa.dnss[1].name == 'ns6.rdns.ar'
    assert wa.dnss[2].name == 'ns1.rdns.ar'
    assert wa.dnss[3].name == 'ns2.rdns.ar'
    assert wa.dnss[4].name == 'ns3.rdns.ar'


@mock.patch('subprocess.Popen')
def test_fernet(mock_subproc_popen):

    wa = WhoAre()    
    mock_subproc_popen.return_value = whois_from_txt('whoare/zone_parsers/ar/sample_fernet.txt')
    wa.load('fernet.com.ar')
    assert mock_subproc_popen.called

    expected_dict = {
        "domain": {
            "base_name": 'fernet',
            "zone": 'com.ar',
            "is_free": False,
            "registered": wa.domain.registered.strftime('%Y-%m-%d %H:%M:%S.%f %z'),
            "changed": wa.domain.changed.strftime('%Y-%m-%d %H:%M:%S.%f %z'),
            "expire": wa.domain.expire.strftime('%Y-%m-%d %H:%M:%S.%f %z')
            },
        "registrant": {
            "name": wa.registrant.name,
            "legal_uid": wa.registrant.legal_uid,
            "created": wa.registrant.created.strftime('%Y-%m-%d %H:%M:%S.%f %z'),
            "changed": wa.registrant.changed.strftime('%Y-%m-%d %H:%M:%S.%f %z')
        },
        "dnss": ['ns2.sedoparking.com', 'ns1.sedoparking.com']
    }
    
    assert wa.as_dict() == expected_dict