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
    'version': '3.0.0.dev20',
    'description': 'Fast probabilistic data linkage at scale',
    'long_description': '# Fast, accurate and scalable probabilistic data linkage using your choice of SQL backend.\n\n![image](https://user-images.githubusercontent.com/7570107/85285114-3969ac00-b488-11ea-88ff-5fca1b34af1f.png)\n\n`splink` is a Python package for probabilistic record linkage (entity resolution).\n\nIts key features are:\n\n- It is extremely fast. It is capable of linking a million records on a laptop in around a minute.\n\n- It is highly accurate, with support for term frequency adjustments, and sophisticated fuzzy matching logic.\n\n- It supports running linkage against multiple SQL backends, meaning it\'s capable of running at any scale. For smaller linkages of up to a few million records, no additional infrastructure is needed . For larger linkages, Splink currently supports Apache Spark or AWS Athena as backends.\n\n- It produces a wide variety of interactive outputs, helping users to understand their model and diagnose linkage problems.\n\nThe core linkage algorithm is an implementation of Fellegi-Sunter\'s canonical model of record linkage, with various customisations to improve accuracy. Splink includes an implementation of the Expectation Maximisation algorithm, meaning that record linkage can be performed using an unsupervised approch (i.e. labelled training data is not needed).\n\n## Documentation\n\nThe homepage for the Splink documentation can be found [here](https://moj-analytical-services.github.io/splink/). Interactive demos can be found [here](https://github.com/moj-analytical-services/splink_demos/tree/splink3_demos), or by clicking the following Binder link:\n[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/moj-analytical-services/splink_demos/splink3_demos?urlpath=lab)\n\nThe specification of the Fellegi Sunter statistical model behind `splink` is similar as that used in the R [fastLink package](https://github.com/kosukeimai/fastLink). Accompanying the fastLink package is an [academic paper](http://imai.fas.harvard.edu/research/files/linkage.pdf) that describes this model. A [series of interactive articles](https://www.robinlinacre.com/probabilistic_linkage/) also explores the theory behind Splink.\n\n## Quickstart\n\nThe following code demonstrates how to estimate the parameters of a deduplication model, and then use it to identify duplicate records.\n\nFor more detailed tutorials, please see [here](https://github.com/moj-analytical-services/splink_demos/tree/splink3_demos).\n\n```\nfrom splink.duckdb.duckdb_linker import DuckDBLinker\nfrom splink.duckdb.duckdb_comparison_library import (\n    exact_match,\n    levenshtein_at_thresholds,\n)\n\nimport pandas as pd\ndf = pd.read_csv("./tests/datasets/fake_1000_from_splink_demos.csv")\n\nsettings = {\n    "link_type": "dedupe_only",\n    "blocking_rules_to_generate_predictions": [\n        "l.first_name = r.first_name",\n        "l.surname = r.surname",\n    ],\n    "comparisons": [\n        levenshtein_at_thresholds("first_name", 2),\n        exact_match("surname"),\n        exact_match("dob"),\n        exact_match("city", term_frequency_adjustments=True),\n        exact_match("email"),\n    ],\n}\n\nlinker = DuckDBLinker(df, settings)\nlinker.estimate_u_using_random_sampling(target_rows=1e6)\n\nblocking_rule_for_training = "l.first_name = r.first_name and l.surname = r.surname"\nlinker.estimate_parameters_using_expectation_maximisation(blocking_rule_for_training)\n\nblocking_rule_for_training = "l.dob = r.dob"\nlinker.estimate_parameters_using_expectation_maximisation(blocking_rule_for_training)\n\nscored_comparisons = linker.predict()\n\n```\n\n## Acknowledgements\n\nWe are very grateful to [ADR UK](https://www.adruk.org/) (Administrative Data Research UK) for providing the initial funding for this work as part of the [Data First](https://www.adruk.org/our-work/browse-all-projects/data-first-harnessing-the-potential-of-linked-administrative-data-for-the-justice-system-169/) project.\n\nWe are also very grateful to colleagues at the UK\'s Office for National Statistics for their expert advice and peer review of this work.\n',
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
