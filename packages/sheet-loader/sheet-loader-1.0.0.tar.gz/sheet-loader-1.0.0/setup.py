# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['sheet_loader']

package_data = \
{'': ['*']}

install_requires = \
['chardet']

extras_require = \
{'pandas': ['pandas']}

setup_kwargs = {
    'name': 'sheet-loader',
    'version': '1.0.0',
    'description': 'Description',
    'long_description': '# sheet-loader\n',
    'author': 'Daniel Sullivan',
    'author_email': 'mumblepins@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/mumblepins/sheet-loader/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
