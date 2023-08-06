# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jahs_bench',
 'jahs_bench.lib',
 'jahs_bench.lib.core',
 'jahs_bench.surrogate',
 'jahs_bench.surrogate_training',
 'jahs_bench.tabular',
 'jahs_bench.tabular.clusterlib',
 'jahs_bench.tabular.lib',
 'jahs_bench.tabular.lib.core',
 'jahs_bench.tabular.lib.naslib',
 'jahs_bench.tabular.lib.naslib.search_spaces',
 'jahs_bench.tabular.lib.naslib.search_spaces.core',
 'jahs_bench.tabular.lib.naslib.utils',
 'jahs_bench.tabular.lib.postprocessing',
 'jahs_bench.tabular.scripts',
 'jahs_bench.tabular.search_space',
 'jahs_bench.tabular.surrogate',
 'jahs_bench_examples']

package_data = \
{'': ['*']}

install_requires = \
['ConfigSpace>=0.4.0,<0.5.0',
 'joblib>=1.1.0,<1.2.0',
 'numpy>=1.21.0,<1.22.0',
 'pandas>=1.3.0,<1.4.0',
 'pyyaml>=5,<6',
 'requests>=2.28.0,<3.0.0',
 'scikit-learn>=1.0.2,<1.1.0',
 'xgboost>=1.5.0,<1.6.0',
 'yacs>=0.1.8,<0.2.0']

setup_kwargs = {
    'name': 'jahs-bench',
    'version': '0.1.0',
    'description': 'The first collection of surrogate benchmarks for Joint Architecture and Hyperparameter Search.',
    'long_description': '# JAHS-Bench-201\n\nThe first collection of surrogate benchmarks for Joint Architecture and Hyperparameter Search (JAHS), built to also support and\nfacilitate research on multi-objective, cost-aware and (multi) multi-fidelity optimization algorithms.\n\n\n![Python versions](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-informational)\n[![License](https://img.shields.io/badge/license-MIT-informational)](LICENSE)\n\nPlease see our [documentation here](https://automl.github.io/jahs_bench_201/).\n\n\n## Installation\n\nUsing pip\n\n```bash\npip install git+https://github.com/automl/jahs_bench_201.git\n```\n\nOptionally, you can download the data required to use the surrogate benchmark ahead of time with\n```bash\npython -m jahs_bench.download --target surrogates\n```\n\nTo test if the installation was successful, you can, e.g, run a minimal example with\n```bash\npython -m jahs_bench_examples.minimal\n```\nThis should randomly sample a configuration, and display both the sampled configuration and the result of querying the\nsurrogate for that configuration.\n\n## Using the Benchmark\n\n### Creating Configurations\n\nConfigurations in our Joint Architecture and Hyperparameter (JAHS) space are represented as dictionaries, e.g.,:\n\n```python\nconfig = {\n    \'Optimizer\': \'SGD\',\n    \'LearningRate\': 0.1,\n    \'WeightDecay\': 5e-05,\n    \'Activation\': \'Mish\',\n    \'TrivialAugment\': False,\n    \'Op1\': 4,\n    \'Op2\': 1,\n    \'Op3\': 2,\n    \'Op4\': 0,\n    \'Op5\': 2,\n    \'Op6\': 1,\n    \'N\': 5,\n    \'W\': 16,\n    \'Resolution\': 1.0,\n}\n```\n\nFor a full description on the search space and configurations see our [documentation](https://automl.github.io/jahs_bench_201/search_space).\n\n\n### Evaluating Configurations\n\n```python\nimport jahs_bench\n\nbenchmark = jahs_bench.Benchmark(task="cifar10", download=True)\n\n# Query a random configuration\nconfig = benchmark.sample_config()\nresults = benchmark(config, nepochs=200)\n\n# Display the outputs\nprint(f"Config: {config}")  # A dict\nprint(f"Result: {results}")  # A dict\n```\n\n\n### More Evaluation Options\n\nThe API of our benchmark enables users to either query a surrogate model (the default) or the tables of performance data, or train a\nconfiguration from our search space from scratch using the same pipeline as was used by our benchmark.\nHowever, users should note that the latter functionality requires the installation of `jahs_bench_201` with the\noptional `data_creation` component and its relevant dependencies. The relevant data can be automatically downloaded by\nour API. See our [documentation](https://automl.github.io/jahs_bench_201/usage) for details.\n\n## Benchmark Data\n\nWe provide [documentation for the performance dataset](https://automl.github.io/jahs_bench_201/performance_dataset) used to train our surrogate models and [further information on our surrogate models](https://automl.github.io/jahs_bench_201/surrogate).\n\n\n## Experiments and Evaluation Protocol\n\nSee [our experiments repository](https://github.com/automl/jahs_bench_201_experiments) and our [documentation](https://automl.github.io/jahs_bench_201/evaluation_protocol).\n\n## Leaderboards\n\nWe maintain [leaderboards](https://automl.github.io/jahs_bench_201/leaderboards) for several optimization tasks and algorithmic frameworks.\n',
    'author': 'Archit Bansal',
    'author_email': 'bansala@cs.uni-freiburg.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/automl/jahs_bench',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<=3.10',
}


setup(**setup_kwargs)
