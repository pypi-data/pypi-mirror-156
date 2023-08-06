# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['abics',
 'abics.applications',
 'abics.applications.latgas_abinitio_interface',
 'abics.scripts']

package_data = \
{'': ['*']}

install_requires = \
['mpi4py>=3,<4',
 'numpy>=1.20,<2.0',
 'pymatgen>=2019.12.3',
 'qe_tools>=1.1,<2.0',
 'scipy>=1,<2',
 'toml>=0.10']

entry_points = \
{'console_scripts': ['abicsRXsepT = abics.scripts.abicsRXsepT:main',
                     'abics_mlref = abics.scripts.activelearn:main',
                     'abics_sampling = abics.scripts.main:main',
                     'abics_train = abics.scripts.train:main',
                     'st2abics = abics.scripts.st2abics_config:main']}

setup_kwargs = {
    'name': 'abics',
    'version': '2.0.0',
    'description': 'ab-Initio Configuration Sampling tool kit',
    'long_description': '# abICS\nabICS is a software framework for training a machine learning model to\nreproduce first-principles energies and then using the model to perform\nconfigurational sampling in disordered systems.\nSpecific emphasis is placed on multi-component solid state systems such as metal and oxide alloys.\nThe current version of abics can use neural network models implemented in aenet to be used as \nthe machine learning model. As of this moment, abICS can also generate Quantum Espresso, VASP, \nand OpenMX input files for obtaining the reference training data for the machine learning model.\n\n## Requirement\n\n- python3 (>=3.7)\n- numpy\n- scipy\n- toml (for parsing input files)\n- mpi4py (for parallel tempering)\n  - This requires one of the MPI implementation\n- pymatgen (>=2019.12.3) (for using Structure as a configuration)\n  - This requires Cython\n- qe-tools (for parsing QE I/O)\n\n## Install abICS\n\nPymatgen requires Cython but Cython will not be installed automatically,\nplease make sure that this is installed,\n\n``` bash\n$ pip3 install Cython\n```\n\nmpi4py requires one of the MPI implementations such as OpenMPI,\nplease make sure that this is also installed.\nIn the case of using homebrew on macOS, for example,\n\n``` bash\n$ brew install open-mpi\n```\n\nAfter installing Cython and MPI,\n\n``` bash\n$ pip3 install abics\n```\n\nwill install abICS and dependencies.\n\nIf you want to change the directory where abICS is installed,\nadd `--user` option or `--prefix=DIRECTORY` option to the above command as\n\n``` bash\n$ pip3 install --user abics\n```\n\nFor details of `pip` , see the manual of `pip` by `pip3 help install`\n\nIf you want to install abICS from source, see [wiki page](https://github.com/issp-center-dev/abICS/wiki/Install)\n\n## License\n\nThe distribution of the program package and the source codes follow GNU General Public License version 3 ([GPL v3](http://www.gnu.org/licenses/gpl-3.0.en.html)). \n\n## Official page\n\nhttps://www.pasums.issp.u-tokyo.ac.jp/abics\n\n## Author\n\nShusuke Kasamatsu, Yuichi Motoyama, Kazuyoshi Yoshimi\n\n## Manual\n\n[English online manual](https://issp-center-dev.github.io/abICS/docs/master/en/html/index.html)\n\n[Japnese online manual](https://issp-center-dev.github.io/abICS/docs/master/ja/html/index.html)\n\n[API reference](https://issp-center-dev.github.io/abICS/docs/api/master/html/index.html)\n',
    'author': 'abICS developers',
    'author_email': 'abics-dev@issp.u-tokyo.ac.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/issp-center-dev/abICS',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
