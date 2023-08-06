# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['splink', 'splink.athena', 'splink.duckdb', 'splink.spark', 'splink.sqlite']

package_data = \
{'': ['*'],
 'splink': ['files/*',
            'files/chart_defs/*',
            'files/chart_defs/del/*',
            'files/external_js/*',
            'files/splink_cluster_studio/*',
            'files/splink_comparison_viewer/*',
            'files/splink_vis_utils/*',
            'files/templates/*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0',
 'altair>=4.2.0,<5.0.0',
 'duckdb==0.3.2',
 'jsonschema>=3.2,<4.0',
 'pandas>=1.0.0,<2.0.0',
 'sqlglot>=2.7.0,<3.0.0']

setup_kwargs = {
    'name': 'splink',
    'version': '3.0.0.dev19',
    'description': 'Fast probabilistic data linkage at scale',
    'long_description': "# Fast, accurate and scalable probabilistic data linkage using your choice of SQL backend.\n\n![image](https://user-images.githubusercontent.com/7570107/85285114-3969ac00-b488-11ea-88ff-5fca1b34af1f.png)\n\n`splink` is a Python package for probabilistic record linkage (entity resolution).\n\nIts key features are:\n\n- It is extremely fast. It is capable of linking a million records on a laptop in around a minute.\n\n- It is highly accurate, with support for term frequency adjustments, and sophisticated fuzzy matching logic.\n\n- It supports running linkage against multiple SQL backends, meaning it's capable of running at any scale. For smaller linkages of up to a few million records, no additional infrastructure is needed . For larger linkages, Splink currently supports Apache Spark or AWS Athena as backends.\n\n- It produces a wide variety of interactive outputs, helping users to understand their model and diagnose linkage problems.\n\nThe core linkage algorithm is an implementation of Fellegi-Sunter's canonical model of record linkage, with various customisations to improve accuracy. Splink includes an implementation of the Expectation Maximisation algorithm, meaning that record linkage can be performed using an unsupervised approch (i.e. labelled training data is not needed).\n\n## Documentation\n\nThe homepage for the Splink documentation can be found [here](https://moj-analytical-services.github.io/splink/). Interactive demos can be found [here](https://github.com/moj-analytical-services/splink_demos/tree/splink3_demos), or by clicking the following Binder link:\n[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/moj-analytical-services/splink_demos/splink3_demos?urlpath=lab)\n\n## Acknowledgements\n\nWe are very grateful to [ADR UK](https://www.adruk.org/) (Administrative Data Research UK) for providing funding for this work as part of the [Data First](https://www.adruk.org/our-work/browse-all-projects/data-first-harnessing-the-potential-of-linked-administrative-data-for-the-justice-system-169/) project.\n\nWe are also very grateful to colleagues at the UK's Office for National Statistics for their expert advice and peer review of this work.\n",
    'author': 'Robin Linacre',
    'author_email': 'robinlinacre@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/moj-analytical-services/splink',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
