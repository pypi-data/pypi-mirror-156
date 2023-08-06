# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dycifer']

package_data = \
{'': ['*']}

install_requires = \
['Markdown>=3.3.7,<4.0.0',
 'argparse>=1.4.0,<2.0.0',
 'colorama>=0.4.5,<0.5.0',
 'loguru>=0.6.0,<0.7.0',
 'matplotlib>=3.5.2,<4.0.0',
 'modelling-utils>=0.2.11,<0.3.0',
 'numpy>=1.22.4,<2.0.0',
 'pandas>=1.4.2,<2.0.0',
 'plotext>=5.0.2,<6.0.0',
 'pyfiglet>=0.8.post1,<0.9',
 'tabulate>=0.8.9,<0.9.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['dycifer = dycifer.dycifer:cli']}

setup_kwargs = {
    'name': 'dycifer',
    'version': '0.1.0',
    'description': 'DYCIFER (Dynamic Circuits Performance Evaluation Tool) is a tool dedicated to the calculation of the performance indicators of integrated circuits operating at relatively high frequencies.',
    'long_description': None,
    'author': 'Diogo André S. Dias',
    'author_email': 'das.dias6@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/das-dias/dyciferpy',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
