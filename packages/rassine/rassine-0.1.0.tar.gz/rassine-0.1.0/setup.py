# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['rassine',
 'rassine.imports',
 'rassine.lib',
 'rassine.matching',
 'rassine.rassine',
 'rassine.stacking',
 'rassine.tools']

package_data = \
{'': ['*']}

install_requires = \
['PyQt5-Qt>=5.15.2,<6.0.0',
 'PyQt5-sip>=12.9.1,<13.0.0',
 'PyQt5>=5.15.6,<6.0.0',
 'astropy>=4.2.1,<5.0.0',
 'configpile[rich,parsy]>=10.0.3,<11.0.0',
 'deepdish>=0.3.7,<0.4.0',
 'filelock>=3.6.0,<4.0.0',
 'h5py>=2.10.0,<3.0.0',
 'matplotlib>=3.3.4,<4.0.0',
 'nptyping>=1.4.4,<2.0.0',
 'numpy>=1.22.3,<2.0.0',
 'pandas>=1.2.4,<2.0.0',
 'parsy>=1.4.0,<2.0.0',
 'recursive-diff>=1.0.0,<2.0.0',
 'rich>=11.2.0,<12.0.0',
 'scipy>=1.6.2,<2.0.0',
 'tybles>=0.3.2,<0.4.0',
 'typeguard>=2.13.3,<3.0.0',
 'typing-extensions>=4.1.1,<5.0.0']

extras_require = \
{'docs': ['ipywidgets>=7.7.0,<8.0.0',
          'myst-nb>=0.15.0,<0.16.0',
          'sphinx==4.5.0',
          'sphinx-argparse>=0.3.1,<0.4.0',
          'sphinx-autodoc-typehints>=1.18.3,<2.0.0',
          'sphinx-book-theme>=0.3.2,<0.4.0',
          'sphinxcontrib-bibtex>=2.4.2,<3.0.0']}

entry_points = \
{'console_scripts': ['enumerate_table_column_unique_values = '
                     'rassine.tools.enumerate_table_column_unique_values:cli',
                     'enumerate_table_rows = '
                     'rassine.tools.enumerate_table_rows:cli',
                     'matching_anchors_filter = '
                     'rassine.matching.matching_anchors_filter:cli',
                     'matching_anchors_scan = '
                     'rassine.matching.matching_anchors_scan:cli',
                     'matching_diff = rassine.matching.matching_diff:cli',
                     'pickle_compare = rassine.tools.pickle_compare:cli',
                     'preprocess_import = '
                     'rassine.imports.preprocess_import:cli',
                     'preprocess_table = rassine.imports.preprocess_table:cli',
                     'rassine = rassine.rassine.rassine:cli',
                     'reinterpolate = rassine.imports.reinterpolate:cli',
                     'reorder_csv = rassine.tools.reorder_csv:cli',
                     'sort_csv = rassine.tools.sort_csv:cli',
                     'stacking_create_groups = '
                     'rassine.stacking.stacking_create_groups:cli',
                     'stacking_master_spectrum = '
                     'rassine.stacking.stacking_master_spectrum:cli',
                     'stacking_stack = rassine.stacking.stacking_stack:cli']}

setup_kwargs = {
    'name': 'rassine',
    'version': '0.1.0',
    'description': 'RASSINE astronomy tool',
    'long_description': '# RASSINE\n\nRASSINE is a tool to ...',
    'author': 'Michael Cretignier',
    'author_email': 'michael.cretignier@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/denisrosset/rassine.git',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
