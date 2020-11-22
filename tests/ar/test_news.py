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
    
    # TODO
    # página rota
    # assert 'accattap-escuela.com.ar' in urls
    #  ... y toma como zona al que sigue
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
    