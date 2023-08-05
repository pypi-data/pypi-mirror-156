# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['s3interactions']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.24.14,<2.0.0',
 'logdecoratorandhandler>=0.1.4,<0.2.0',
 'moto>=3.1.14,<4.0.0',
 'pandas>=1.4.2,<2.0.0',
 'pydicom>=2.3.0,<3.0.0',
 'pytest>=7.1.2,<8.0.0']

setup_kwargs = {
    'name': 's3interactions',
    'version': '0.1.0',
    'description': 'Some most important interactions with S3 AWS',
    'long_description': None,
    'author': 'barbara73',
    'author_email': 'barbara.jesacher@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
