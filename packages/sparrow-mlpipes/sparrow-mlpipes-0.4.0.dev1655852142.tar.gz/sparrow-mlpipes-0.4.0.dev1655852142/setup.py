# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sparrow_mlpipes', 'sparrow_mlpipes.bins']

package_data = \
{'': ['*']}

install_requires = \
['aioboto3==9.5.0',
 'aiobotocore==2.2.0',
 'boto3==1.21.21',
 'botocore==1.24.21',
 'dvc[s3]>=2.10.2,<3.0.0',
 'fire>=0.4.0,<0.5.0',
 'numpy>=1.21.4,<2.0.0',
 's3fs==2022.3.0',
 's3transfer==0.5.2',
 'scipy>=1.8.1,<2.0.0']

setup_kwargs = {
    'name': 'sparrow-mlpipes',
    'version': '0.4.0.dev1655852142',
    'description': 'Tools for Nvidia DeepStream',
    'long_description': None,
    'author': 'jbencook',
    'author_email': 'ben@sparrow.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
