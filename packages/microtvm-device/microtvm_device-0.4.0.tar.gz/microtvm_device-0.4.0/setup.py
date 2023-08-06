# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['microtvm_device']

package_data = \
{'': ['*']}

install_requires = \
['grpcio-tools>=1.39.0,<2.0.0',
 'grpcio>=1.39.0,<2.0.0',
 'pytest>=6.2.4,<7.0.0',
 'tabulate>=0.8.9,<0.9.0']

setup_kwargs = {
    'name': 'microtvm-device',
    'version': '0.4.0',
    'description': '',
    'long_description': '# MicroTVM Device Python Package\n\nA python package for managing microTVM devices on a server for the purpose of hardware CI testing, autotuning, etc.\n\n## Installation\n\n```\npip3 install microtvm_device\n```\n\n## Setup Device Server\nTo run the device server run command bellow with a JSON file including information about various devices. [Here](./config/device_table.template.json) is a template of JSON file.\n```\npython -m microtvm_device.device_server --table-file=[DEVICE TABLE JSON FILE] <--port=[SERVER PORT]>\n\nNote: If you are using the server in an envrionment with multiple users using VirtualBox, server should be run on an account with `sudo` access to all account to be able to inquery the USB attachments with any VirtualBox instance.\n```\n\n## Use Device Client\n\nAfter running server you can run various command using device_client. Command includes `attach`, `detach`, `release`, `request` and `query`.\n\n```\npython -m microtvm_device.device_client <--port=[SERVER PORT]> COMMAND \n```\n',
    'author': 'mehrdadh',
    'author_email': 'mehrdad.hessar@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mehrdadh/microtvm-device',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
