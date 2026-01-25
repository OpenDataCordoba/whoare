from whoare.zone_parsers.ar.news import NewDomains


def read_pdf(date_str):
    nd = NewDomains()
    nd.data_path = 'tests/ar/samples'
    results = nd.get_from_date(date_str)

    urls = []
    for zona, lista in results['zonas'].items():
        for dom in lista:
            urls.append(dom)
    return urls

def test_new_domains_01_04_2020():
    urls = read_pdf('01-04-2020')

    assert '25casacobre.ar' in urls
    assert 'casaelefante.ar' in urls
    assert '11directo.com.ar' in urls

    # TODO, no lo ve
    # assert 'accattap-escuela.com.ar' in urls
    # assert 'acequiaargentina.com.ar' in urls

    assert 'alejandrocura.com.ar' in urls
    assert 'alejandroshifman.com.ar' in urls
    assert 'rinowinestudiodediseño.com.ar' in urls
    assert 'zonazerocomputacion.com.ar' in urls
    assert 'ñemity.com.ar' in urls
    assert 'calchaqui.gob.ar' in urls
    assert 'academica.net.ar' in urls
    assert 'caminandoutopias.org.ar' in urls

    # TODO no veo el titulo de la zona tur.ar
    # podría inferirla leyendo el indice al principio?
    # podría saber que TUR viene despues de ORG?
    # assert 'jungle.tur.ar' in urls

    assert 'adrianaszarfer.com.ar' in urls
    assert 'ar-testing-201.com.ar' in urls


def test_new_domains_01_10_2019():
    urls = read_pdf('01-10-2019')

    assert '111.com.ar' in urls
    assert '13.com.ar' in urls
    assert 'administracionjsa.com.ar' in urls
    assert 'df.com.ar' in urls
    assert 'zray.com.ar' in urls
    assert 'fiestanacionaldelalfajor.gob.ar' in urls
    assert 'ambar.net.ar' in urls
    assert 'b.net.ar' in urls
    assert 'aecpa.org.ar' in urls
    assert 'acarizax.com.ar' in urls
    assert 'delpilar-evt.com.ar' in urls


def test_new_domains_16_09_2020():
    urls = read_pdf('16-09-2020')

    # TODO no los ve ...
    assert 'distribat.ar' in urls
    assert 'santafe.ar' in urls
    assert '123listatuweb.com.ar' in urls
    assert 'abef-srl.com.ar' in urls
    assert 'aljazeera.com.ar' in urls
    assert 'anabellapañalera.com.ar' in urls
    assert 'diccionariovirtualdeartistasvisualesargentinos.com.ar' in urls
    assert 'zoopets.com.ar' in urls
    assert 'zuzu.com.ar' in urls
    assert 'angelvicentepenaloza.gob.ar' in urls
    assert '45millones.net.ar' in urls
    assert 'elmanantial.net.ar' in urls
    assert 'aadeca2020.org.ar' in urls
    assert 'altitudnorte.tur.ar' in urls
    assert 'alfarack.com.ar' in urls


def test_new_domains_17_02_2020():
    urls = read_pdf('17-02-2020')

    assert '1000cursos.com.ar' in urls
    assert 'codexsanjuan.com.ar' in urls
    assert 'informaticat.com.ar' in urls
    assert 'zaratenoticias.com.ar' in urls
    assert 'laagencia.net.ar' in urls
    assert 'buenosairesfreetour.com.ar' in urls


def test_new_domains_18_08_2020():
    urls = read_pdf('18-08-2020')

    assert '1000oportunidades.com.ar' in urls
    # que necesidad?
    assert 'acompañanteterapéutico.com.ar' in urls
    assert 'flämmen.com.ar' in urls
    # pagina rota
    # assert 'h3o.com.ar' in urls
    assert 'zumdrone.com.ar' in urls
    assert 'cdcampoquijano.gob.ar' in urls
    assert 'appcriptoarg.net.ar' in urls
    assert 'worldtech.net.ar' in urls
    assert 'bomberosjesusmaria.org.ar' in urls
    assert 'todoshacemosmusica.org.ar' in urls
    assert 'allpeninsulavaldes.tur.ar' in urls
    assert 'previaje.tur.ar' in urls
    assert 'akita.com.ar' in urls
