# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torchdyn',
 'torchdyn.core',
 'torchdyn.datasets',
 'torchdyn.models',
 'torchdyn.nn',
 'torchdyn.numerics',
 'torchdyn.numerics.solvers']

package_data = \
{'': ['*']}

install_requires = \
['ipykernel',
 'ipywidgets',
 'matplotlib',
 'poethepoet>=0.10.0,<0.11.0',
 'pytorch-lightning',
 'scipy',
 'sklearn',
 'torch>=1.8.1,<2.0.0',
 'torchcde>=0.2.3,<0.3.0',
 'torchsde',
 'torchvision']

setup_kwargs = {
    'name': 'torchdyn',
    'version': '1.0.3',
    'description': 'A PyTorch library entirely dedicated to neural differential equations, implicit models and related numerical methods.',
    'long_description': None,
    'author': 'Michael Poli',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
