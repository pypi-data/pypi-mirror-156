# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyarr', 'pyarr.models']

package_data = \
{'': ['*']}

modules = \
['py']
install_requires = \
['requests>=2.21.0,<3.0.0', 'types-requests>=2.25.11,<3.0.0']

setup_kwargs = {
    'name': 'pyarr',
    'version': '4.0.2',
    'description': "Synchronous Sonarr, Radarr, Lidarr and Readarr API's for Python",
    'long_description': "# Sonarr and Radarr API Python Wrapper\n\nPython Wrapper for the [Sonarr](https://github.com/Sonarr/Sonarr), [Radarr](https://github.com/Radarr/Radarr), [Lidarr](https://github.com/Lidarr/Lidarr) & [Readarr](https://github.com/Readarr/Readarr) API.\n\nSee the full [documentation](https://docs.totaldebug.uk/pyarr/) for supported functions.\n\n### Requirements\n\n-   requests\n\n### Example Sonarr Usage:\n\n```python\n# Import SonarrAPI Class\nfrom pyarr import SonarrAPI\n\n# Set Host URL and API-Key\nhost_url = 'http://your-domain.com'\n\n# You can find your API key in Settings > General.\napi_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'\n\n# Instantiate SonarrAPI Object\nsonarr = SonarrAPI(host_url, api_key)\n\n# Get and print TV Shows\nprint(sonarr.get_series(123))\n```\n\n### Example Radarr Usage:\n\n```python\n# Import RadarrAPI Class\nfrom pyarr import RadarrAPI\n\n# Set Host URL and API-Key\nhost_url = 'http://your-domain.com'\n\n# You can find your API key in Settings > General.\napi_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'\n\n# Instantiate RadarrAPI Object\nradarr = RadarrAPI(host_url, api_key)\n\n# Get and print TV Shows\nprint(radarr.get_root_folder())\n```\n\n### Documentation\n\n-   [Pyarr Documentation](https://docs.totaldebug.uk/pyarr)\n-   [Sonarr API Documentation](https://github.com/Sonarr/Sonarr/wiki/API)\n-   [Radarr API Documentation](https://radarr.video/docs/api)\n",
    'author': 'Steven Marks',
    'author_email': 'marksie1988@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/totaldebug/pyarr',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
