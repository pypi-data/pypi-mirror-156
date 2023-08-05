# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['falconcv',
 'falconcv.cons',
 'falconcv.data',
 'falconcv.data.scrapping',
 'falconcv.decor',
 'falconcv.models',
 'falconcv.models.detectron',
 'falconcv.models.toda',
 'falconcv.util']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.27,<4.0.0',
 'Mako>=1.2.0,<2.0.0',
 'Pillow>=9.1.1,<10.0.0',
 'alive-progress>=2.4.1,<3.0.0',
 'boto3>=1.24.13,<2.0.0',
 'bs4>=0.0.1,<0.0.2',
 'dask[complete]==2.30.0',
 'lxml>=4.9.0,<5.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'opencv-python>=4.6.0,<5.0.0',
 'pandas<=1.3.5',
 'pyparsing==2.4.2',
 'requests>=2.28.0,<3.0.0',
 'rich>=12.4.4,<13.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'tensorflow>=2.9.1,<3.0.0',
 'tflite-support>=0.4.1,<0.5.0',
 'typing-extensions>=4.2.0,<5.0.0',
 'validators>=0.20.0,<0.21.0']

setup_kwargs = {
    'name': 'falconcv',
    'version': '1.0.4',
    'description': '',
    'long_description': None,
    'author': 'Henry Ruiz',
    'author_email': 'henry.ruiz@tamu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<3.8.0',
}


setup(**setup_kwargs)
