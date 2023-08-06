# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['paf_sapgui_tc_zfmta_rar']

package_data = \
{'': ['*']}

install_requires = \
['paf_sapgui>=1.0.18,<2.0.0',
 'paf_sapgui_eltrans>=1.0.8,<2.0.0',
 'paf_tools>=0.3.3,<0.4.0',
 'pendulum>=2.1.2,<3.0.0']

setup_kwargs = {
    'name': 'paf-sapgui-tc-zfmta-rar',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
