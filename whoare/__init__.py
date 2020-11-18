package_name = 'whoare'
__version__ = '0.1.40'

def require_update_pypi():
    import requests
    response = requests.get(f'https://pypi.org/pypi/{package_name}/json')
    data = response.json()
    pypi_version = data['info']['version']

    return pypi_version != __version__
