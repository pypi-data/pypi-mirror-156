# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['isecycle']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'PyYAML>=6.0,<7.0',
 'gTTS>=2.2.4,<3.0.0',
 'requests>=2.28.0,<3.0.0',
 'rich-click>=1.5.1,<2.0.0',
 'rich>=12.4.4,<13.0.0',
 'xmltodict>=0.13.0,<0.14.0']

entry_points = \
{'console_scripts': ['isecycle = isecycle.script:run']}

setup_kwargs = {
    'name': 'isecycle',
    'version': '1.0.0',
    'description': 'Business Ready Documents from Cisco Identity Services Engine',
    'long_description': '# isecycle\nBusiness Ready Documents from Cisco Identity Services Engine\n',
    'author': 'John Capobianco',
    'author_email': 'ptcapo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
