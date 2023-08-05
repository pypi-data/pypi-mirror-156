# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['onemodel_cli']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.0,<9.0.0', 'onemodel>=0.2.0,<0.3.0']

entry_points = \
{'console_scripts': ['onemodel-cli = onemodel_cli.cli:main']}

setup_kwargs = {
    'name': 'onemodel-cli',
    'version': '0.1.0',
    'description': 'A command-line interface for OneModel',
    'long_description': '# SBML2dae: a customizable SBML to Matlab parser\n\n[![GitHub Actions][github-actions-badge]](https://github.com/sb2cl/onemodel-cli/actions)\n[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)\n\n[github-actions-badge]: https://github.com/sb2cl/onemodel-cli/workflows/python/badge.svg\n\n## Description\n\n`onemodel-cli` is a command-line interface for the functionality of [OneModel](https://github.com/sb2cl/onemodel).\n\n## Motivation\n\nOneModel can be used as a stand-alone package within a Python project. However, for `onemodel-cli` streamlines using OneModel for an expert users and simplies integrating OneModel into pre-existing workflows.\n\n## How to setup\n\n`onemodel-cli` can be installed from PyPI and is compatible with Python 3.7+ for Window, Mac and Linux.\n\nThe latest package can be installed with:\n\n```sh\npip install onemodel-cli\n```\n\n## Quick example\n\nTODO\n\n## Citing\n\nIf you use `onemodel-cli` in your research, please use the following citations in your published works:\n\n- Santos-Navarro, F. N., Navarro, J. L., Boada, Y., Vignoni, A., & Picó, J. (2022). "OneModel: an open-source SBML modeling tool focused on accessibility, simplicity, and modularity." *DYCOPS*.\n\n- Santos-Navarro, F. N., Vignoni, A., & Picó, J. (2022). "Multi-scale host-aware modeling for analysis and tuning of synthetic gene circuits for bioproduction." *PhD thesis*.\n\n## License\n\nCopyright 2022 Fernando N. Santos-Navarro, Jose Luis Herrero, Yadira Boada, Alejandro Vignoni, and Jesús Picó\n\nLicensed under the Apache License, Version 2.0 (the "License"); you may not use this software except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.\n',
    'author': 'Fernando N. Santos Navarro',
    'author_email': 'fersann1@upv.es',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sb2cl/onemodel-cli',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
