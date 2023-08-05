# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['geolib_plus',
 'geolib_plus.bro_xml_cpt',
 'geolib_plus.cpt_utils',
 'geolib_plus.gef_cpt',
 'geolib_plus.robertson_cpt_interpretation',
 'geolib_plus.shm']

package_data = \
{'': ['*'],
 'geolib_plus.cpt_utils': ['resources/*'],
 'geolib_plus.gef_cpt': ['resources/*'],
 'geolib_plus.robertson_cpt_interpretation': ['resources/*'],
 'geolib_plus.shm': ['resources/*']}

install_requires = \
['Shapely>=1.8,<2.0',
 'd-geolib>=0.1,<0.2',
 'lxml>=4.7,<5.0',
 'matplotlib>=3.4,<4.0',
 'more-itertools>=8.6,<9.0',
 'netCDF4>=1.5,<2.0',
 'numpy>=1.19,<2.0',
 'pandas>=1.4,<2.0',
 'pydantic>=1,<2',
 'pyproj>=3.3,<4.0',
 'pyshp>=2.1,<3.0',
 'requests>=2.26,<3.0',
 'scipy>=1.6,<2.0',
 'tqdm>=4,<5']

setup_kwargs = {
    'name': 'd-geolib-plus',
    'version': '0.1.2',
    'description': 'GEOLib+ components',
    'long_description': None,
    'author': 'Maarten Pronk',
    'author_email': 'git@evetion.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
