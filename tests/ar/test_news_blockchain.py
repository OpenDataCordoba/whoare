from datetime import date
from whoare.zone_parsers.ar.news_from_blockchain import NewDomains


def read_csv(dated):
    nd = NewDomains()
    nd.data_path = 'tests/ar/samples'
    results = nd.get_from_date(dated)

    urls = []
    for zona, lista in results['zonas'].items():
        for dom in lista:
            urls.append(dom)
    return urls


def test_new_domains_2020_12_15():
    urls = read_csv(date(2020, 12, 15))

    assert 'd2creativos.com.ar' in urls
    assert 'danielojeda.com.ar' in urls
    assert 'deseame.ar' in urls
    assert 'desstek.com.ar' in urls
    assert 'diamondprotein.ar' in urls
    assert 'diamondprotein.com.ar' in urls
    assert 'diarioelliberal.ar' in urls


def test_new_domains_2020_12_20():
    urls = read_csv(date(2020, 12, 20))

    assert 'xaragon.com.ar' in urls
    # # xn--expodiseo-s6a.com.ar
    assert 'expodiseño.com.ar' in urls

    assert 'zion.ar' in urls


def test_new_domains_2018_10_08():
    urls = read_csv(date(2018, 10, 8))

    # TODO si empieza con cero el CSV viene malo
    # assert '341.com.ar' in urls
    assert 'abogadosdecordoba.net.ar' in urls
    assert 'abogadosdepueblosfumigados.com.ar' in urls
    assert 'aesucm.org.ar' in urls
    assert 'agenciatimonel.com.ar' in urls
    assert 'agustinpayges.com.ar' in urls
    assert 'forastero.tur.ar' in urls
    assert 'patinesconi.com.ar' in urls
    assert 'pcyrma.org.ar' in urls
    # # xn--diseowebrosario-1qb	com.ar
    assert 'diseñowebrosario.com.ar' in urls
    # # xn--santuariodelapea-lub	com.ar
    assert 'santuariodelapeña.com.ar' in urls


def test_new_domains_2020_11_26():
    urls = read_csv(date(2020, 11, 26))

    assert 'sanro.ar' in urls
    # xn--cabaasatrapasueos-ixbl	com.ar
    assert 'cabañasatrapasueños.com.ar' in urls
    assert 'zenlab.com.ar' in urls


def test_new_domains_2019_01_15():
    urls = read_csv(date(2019, 1, 15))

    assert 'wtracker.com.ar' in urls
    # xn--tartamudezenaccin-vyb	com.ar
    assert 'tartamudezenacción.com.ar' in urls
    assert 'yoquierocalzados.com.ar' in urls
