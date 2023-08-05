# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ansible_docker_ci',
 'ansible_docker_ci.image',
 'ansible_docker_ci.image.connection']

package_data = \
{'': ['*']}

install_requires = \
['class-interference>=1.1.0,<2.0.0', 'docker>=5.0.3,<6.0.0']

setup_kwargs = {
    'name': 'ansible-docker-ci',
    'version': '1.0.0',
    'description': 'Docker image-based dynamic hosts CI utilites for ansible',
    'long_description': '# ansible-docker-ci\n\nDocker image-based dynamic hosts for ansible.\n\n## Installation\n\n```shell\n# Install python package\npip install ansible-docker-ci\n# Add plugin file it your connection plugins directory\necho "from ansible_docker_ci.image.connection.plugin import *" > ./connection_plugins/docker_image.py\n```\n',
    'author': 'Artem Novikov',
    'author_email': 'artnew@list.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/reartnew/ansible-docker-ci',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
