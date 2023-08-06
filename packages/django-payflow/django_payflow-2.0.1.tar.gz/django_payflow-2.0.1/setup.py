# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_payflow']

package_data = \
{'': ['*']}

install_requires = \
['django>=3.2,<4.0', 'requests>=2.28.0,<3.0.0']

setup_kwargs = {
    'name': 'django-payflow',
    'version': '2.0.1',
    'description': 'A django app for interaction with the django_payflow api',
    'long_description': "## Settings \n\ndjango_payflow accepts a python dictionary for all settings \n\nThe minimum settings needed are shown below:\n\n```\nDJANGO_PAYFLOW = {\n    'PARTNER': 'partner', #This will most likely be 'PayPal'\n    'MERCHANT_LOGIN': 'merchant',\n    'USER': 'user', # This will most likely be the same as the MERCHANT_LOGIN setting\n    'PASSWORD': 'password',\n    'TEST_MODE': True,\n}\n```\n",
    'author': 'Imagescape',
    'author_email': 'info@imagescape.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ImaginaryLandscape/django_payflow',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
