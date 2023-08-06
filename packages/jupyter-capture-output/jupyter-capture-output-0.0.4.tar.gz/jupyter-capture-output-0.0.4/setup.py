# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jupyter_capture_output']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.0', 'ipykernel>=5.0.0', 'ipython>=6.0.0']

setup_kwargs = {
    'name': 'jupyter-capture-output',
    'version': '0.0.4',
    'description': 'Capture output from JupyterLab',
    'long_description': None,
    'author': 'kolibril13',
    'author_email': '44469195+kolibril13@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
