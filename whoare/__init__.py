__version__ = '0.1.30'

# env:
#   global:
#     - PYPI_VERSION=wget -qO- https://pypi.org/pypi/whoare/json | jq '.info.version'
#     - HERE_VERSION=echo -e "from whoare import __version__\nprint(f'\"{__version__}\"')" | python
