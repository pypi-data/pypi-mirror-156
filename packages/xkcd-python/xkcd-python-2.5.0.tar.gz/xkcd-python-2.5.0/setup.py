# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xkcd_python']

package_data = \
{'': ['*']}

install_requires = \
['Pygments==2.12.0',
 'atomicwrites==1.4.0',
 'attrs==21.4.0',
 'bleach==5.0.0',
 'certifi==2022.6.15',
 'charset-normalizer==2.0.12',
 'colorama==0.4.5',
 'commonmark==0.9.1',
 'docutils==0.18.1',
 'idna==3.3',
 'importlib-metadata==4.11.4',
 'iniconfig==1.1.1',
 'keyring==23.6.0',
 'packaging==21.3',
 'pkginfo==1.8.3',
 'pluggy==1.0.0',
 'py==1.11.0',
 'pyparsing==3.0.9',
 'pytest==7.1.2',
 'pywin32-ctypes==0.2.0',
 'readme-renderer==35.0',
 'requests-toolbelt==0.9.1',
 'requests==2.28.0',
 'rfc3986==2.0.0',
 'rich==12.4.4',
 'six==1.16.0',
 'tomli==2.0.1',
 'twine==4.0.1',
 'urllib3==1.26.9',
 'webencodings==0.5.1',
 'zipp==3.8.0']

setup_kwargs = {
    'name': 'xkcd-python',
    'version': '2.5.0',
    'description': "A wrapper for xkcd.com's API. Built Using Python.",
    'long_description': '# xkcd-python\n\nxkcd-python is an API wrapper for xkcd.com written in python.\n\n## Installation\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.\n\n```bash\npip install -U xkcd-python\n```\n\n## Usage\n\n```python\nfrom xkcd_python import *\n\n#creates the client\nclient = Client()\n\n# returns the comic by id\nclient.get(1)\n\n# returns a random comic\nclient.random()\n\n# returns the latest comic\nclient.latest_comic()\n```\n\n## Contributing\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nPlease make sure to update tests as appropriate.\n\n## License\n[MIT](https://github.com/Sas2k/xkcd-python/blob/main/LICENSE)',
    'author': 'Sasen Perera',
    'author_email': 'sasen.learnings@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
