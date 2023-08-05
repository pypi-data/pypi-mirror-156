# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['onemodel_gui',
 'onemodel_gui.controllers',
 'onemodel_gui.model',
 'onemodel_gui.views',
 'onemodel_gui.widgets']

package_data = \
{'': ['*']}

install_requires = \
['onemodel-cli>=0.1.0,<0.2.0']

entry_points = \
{'console_scripts': ['onemodel-gui = onemodel_gui.app:main']}

setup_kwargs = {
    'name': 'onemodel-gui',
    'version': '0.1.0',
    'description': 'A graphical user interface for OneModel',
    'long_description': '# onemodel-gui: a graphical user interface for OneModel\n\n[![GitHub Actions][github-actions-badge]](https://github.com/sb2cl/onemodel-gui/actions)\n[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)\n\n[github-actions-badge]: https://github.com/sb2cl/onemodel-gui/workflows/python/badge.svg\n\n## Description\n\n`onemodel-gui` is a graphical user interface for OneModel.\n\n## Motivation\n\nOneModel can be used as a Python package or as a command-line interface (`onemodel-cli`), but both options are aimed for expert users with Python programming knowledge. `onemodel-gui` is aimed for non-experts users: it is the best way to start working with OneModel.\n\n## How to setup\n\n`onemodel-gui` can be installed from PyPI and is compatible with Python 3.7+ for Window, Mac and Linux.\n\nThe latest package can be installed with:\n\n```sh\npip install onemodel-gui\n```\n\n## Quick example\n\nTODO\n\n## Citing\n\nIf you use `onemodel-gui` in your research, please use the following citations in your published works:\n\n- Santos-Navarro, F. N., Navarro, J. L., Boada, Y., Vignoni, A., & Picó, J. (2022). "OneModel: an open-source SBML modeling tool focused on accessibility, simplicity, and modularity." *DYCOPS*.\n\n- Santos-Navarro, F. N., Vignoni, A., & Picó, J. (2022). "Multi-scale host-aware modeling for analysis and tuning of synthetic gene circuits for bioproduction." *PhD thesis*.\n\n## License\n\nCopyright 2022 Fernando N. Santos-Navarro, Jose Luis Herrero, Yadira Boada, Alejandro Vignoni, and Jesús Picó\n\nLicensed under the Apache License, Version 2.0 (the "License"); you may not use this software except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.\n',
    'author': 'Fernando N. Santos Navarro',
    'author_email': 'fersann1@upv.es',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sb2cl/onemodel-gui',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
