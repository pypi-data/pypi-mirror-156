# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['graphysio',
 'graphysio.algorithms',
 'graphysio.plotwidgets',
 'graphysio.readdata',
 'graphysio.ui',
 'graphysio.writedata']

package_data = \
{'': ['*']}

install_requires = \
['Pint>=0.19.2,<0.20.0',
 'attrs>=21.4.0,<22.0.0',
 'numexpr>=2.8.3,<3.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pathvalidate>=2.5.0,<3.0.0',
 'physiocurve>=2022.6.26,<2023.0.0',
 'pyqtgraph>=0.12.4,<0.13.0',
 'scipy>=1.8.1,<2.0.0']

entry_points = \
{'console_scripts': ['graphysio = graphysio.main:main']}

setup_kwargs = {
    'name': 'graphysio',
    'version': '2022.6.26',
    'description': 'Visualizer and analyser for biometric signals',
    'long_description': '# GraPhysio\nGraPhysio is a graphical time series visualizer created for physiologic\ndata signals from ICU patient monitors. It is however not limited to this.\nIt currently supports reading from CSV files.\nIt can handle low frequency and high frequency data as well as aggregating\nand synchronizing signals from different sources.\nGraPhysio supports basic mathematical operations and filters and can help\nselecting and exporting time periods.\nPerformance is good depending on your hardware for files up to 1 GB.\n\n## Install instructions\nTo make GraPhysio work you need Python 3.6 or greater.\n\nYou can then install the latest version of GraPhysio by tying the\nfollowing command:\n\n> python -m pip install graphysio\n\nYou can launch GraPhysio by typing:\n\n> python -m graphysio\n\nAlternatively, on Windows, you can use the release binaries.\n',
    'author': 'Jona Joachim',
    'author_email': 'jona@joachim.cc',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jaj42/GraPhysio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
