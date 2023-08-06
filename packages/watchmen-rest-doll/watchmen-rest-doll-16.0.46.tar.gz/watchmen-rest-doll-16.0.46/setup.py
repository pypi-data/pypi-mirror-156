# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['watchmen_rest_doll',
 'watchmen_rest_doll.admin',
 'watchmen_rest_doll.analysis',
 'watchmen_rest_doll.auth',
 'watchmen_rest_doll.console',
 'watchmen_rest_doll.gui',
 'watchmen_rest_doll.meta_import',
 'watchmen_rest_doll.system',
 'watchmen_rest_doll.util']

package_data = \
{'': ['*']}

install_requires = \
['bcrypt>=3.2.0,<4.0.0',
 'passlib>=1.7.4,<2.0.0',
 'python-multipart>=0.0.5,<0.0.6',
 'watchmen-data-surface==16.0.46',
 'watchmen-inquiry-surface==16.0.46',
 'watchmen-pipeline-surface==16.0.46']

extras_require = \
{'mongodb': ['watchmen-storage-mongodb==16.0.46'],
 'mssql': ['watchmen-storage-mssql==16.0.46'],
 'mysql': ['watchmen-storage-mysql==16.0.46'],
 'oracle': ['watchmen-storage-oracle==16.0.46'],
 'trino': ['watchmen-inquiry-trino==16.0.46']}

setup_kwargs = {
    'name': 'watchmen-rest-doll',
    'version': '16.0.46',
    'description': '',
    'long_description': None,
    'author': 'botlikes',
    'author_email': '75356972+botlikes456@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
