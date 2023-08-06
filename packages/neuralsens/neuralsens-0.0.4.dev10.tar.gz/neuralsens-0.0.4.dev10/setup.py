# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['neuralsens']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.2,<4.0.0',
 'numpy>=1.22.4,<2.0.0',
 'pandas>=1.4.2,<2.0.0',
 'scipy>=1.8.1,<2.0.0']

setup_kwargs = {
    'name': 'neuralsens',
    'version': '0.0.4.dev10',
    'description': 'Calculate word counts in a text file.',
    'long_description': '# NeuralSens <img src="docs/source/_static/NeuralSens.PNG" width="135px" height="140px" align="right" style="padding-left:10px;background-color:white;" />\n\n#### *Jaime Pizarroso Gonzalo, jpizarroso@comillas.edu*\n#### *Antonio Muñoz San Roque, Antonio.Munoz@iit.comillas.edu*\n#### *José Portela González, jose.portela@iit.comillas.edu*\n<!-- badges: start -->\n\n[![Documentation Status](https://readthedocs.org/projects/neuralsens/badge/?version=latest)](https://neuralsens.readthedocs.io/en/latest/?version=latest)\n[![pypi](https://img.shields.io/pypi/v/neuralsens.svg)](https://pypi.python.org/pypi/neuralsens)\n[![python](https://img.shields.io/badge/python-%5E3.8-blue)]()\n[![os](https://img.shields.io/badge/OS-Ubuntu%2C%20Mac%2C%20Windows-purple)]()\n<!-- badges: end -->\nThis is the development repository for the neuralsens package.  Functions within this package can be used for the analysis of neural network models created in Python. \n\nThe last version of this package can be installed using pip:\n\n```bash\n$ pip install neuralsens\n```\n\n### Bug reports\n\nPlease submit any bug reports (or suggestions) using the [issues](https://github.com/JaiPizGon/NeuralSens/issues) tab of the GitHub page.\n\n### Functions\n\nTO DO\n\n### Citation\n\nPlease, to cite NeuralSens in publications use:\n\nPizarroso J, Portela J, Muñoz A (2022). “NeuralSens: Sensitivity Analysis of Neural Networks.” _Journal of\nStatistical Software_, *102*(7), 1-36. doi: 10.18637/jss.v102.i07 (URL:\nhttps://doi.org/10.18637/jss.v102.i07).\n\n### License\n\nThis package is released in the public domain under the General Public License [GPL](https://www.gnu.org/licenses/gpl-3.0.en.html). \n\n### Association\nPackage created in the Institute for Research in Technology (IIT), [link to homepage](https://www.iit.comillas.edu/index.php.en) \n',
    'author': 'Jaime Pizarroso Gonzalo',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/JaiPizGon/NeuralSens',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
