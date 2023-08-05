# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['project_config',
 'project_config.config',
 'project_config.config.style',
 'project_config.fetchers',
 'project_config.plugins',
 'project_config.reporters',
 'project_config.serializers']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1,<2',
 'colored',
 'diskcache>=5,<6',
 'identify>=2,<3',
 'importlib-metadata-argparse-version',
 'jmespath>=1,<2',
 'pyjson5',
 'ruamel.yaml>=0.17,<0.18',
 'tabulate>=0.8,<0.9',
 'tomli-w>=1,<2',
 'typing-extensions>=4,<5']

extras_require = \
{':python_version < "3.10"': ['importlib-metadata'],
 ':python_version < "3.11"': ['tomli>=2,<3']}

entry_points = \
{'console_scripts': ['project-config = project_config.__main__:main'],
 'project_config.plugins': ['include = '
                            'project_config.plugins.include:IncludePlugin',
                            'jmespath = '
                            'project_config.plugins.jmespath:JMESPathPlugin']}

setup_kwargs = {
    'name': 'project-config',
    'version': '0.1.0',
    'description': 'Reproducible configuration across projects.',
    'long_description': '# project-config\n',
    'author': 'Álvaro Mondéjar Rubio',
    'author_email': 'mondejar1994@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/mondeja/project-config',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
