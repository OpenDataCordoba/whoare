PYPI_VERSION=$(wget -qO- https://pypi.org/pypi/whoare/json | jq '.info.version')
HERE_VERSION=$(echo -e "from whoare import __version__\nprint(f'\"{__version__}\"')" | python)

if [$PYPI_VERSION == $HERE_VERSION] 
then 
    REQUIRE_PYPI_UPDATE=false
else
    REQUIRE_PYPI_UPDATE=true
fi