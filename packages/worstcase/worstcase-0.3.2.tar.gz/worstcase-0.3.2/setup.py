# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['worstcase']

package_data = \
{'': ['*']}

install_requires = \
['Pint>=0.17,<0.18', 'networkx>=2.5.1,<3.0.0', 'pyDOE>=0.3.8,<0.4.0']

setup_kwargs = {
    'name': 'worstcase',
    'version': '0.3.2',
    'description': 'Worst case analysis and sensitivity studies using Extreme Value and/or Monte Carlo methods.',
    'long_description': '# worstcase\n\n## Overview\n\n`pip install worstcase`\n\nWorst case analysis and sensitivity studies using Extreme Value and/or Monte Carlo methods.\n\nThis package coexists alongside far more capable uncertainty analysis and error propagation packages such as [uncertainties](https://pypi.org/project/uncertainties/) (first-order propagation), [soerp](https://pypi.org/project/soerp/) (second-order propagation), and [mcerp](https://pypi.org/project/mcerp/) (Monte Carlo propagation).\n\nThis package is designed for engineering applications where worst case analysis computations are often done using the Extreme Value method over single-valued functions while falling back to the Monte Carlo method when the worst case is known to not exist at the extremes. The Extreme Value method is implemented as a brute-force search; the Monte Carlo method is implemented with Latin Hypercube Sampling over a uniform distribution.\n\n## Usage\n\nSee the example usage [here](https://github.com/amosborne/worstcase/blob/master/examples/readme.ipynb).\n',
    'author': 'amosborne',
    'author_email': 'amosborne@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/amosborne/worstcase',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
