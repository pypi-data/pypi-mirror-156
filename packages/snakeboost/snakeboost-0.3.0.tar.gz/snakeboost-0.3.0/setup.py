# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['snakeboost', 'snakeboost.bash']

package_data = \
{'': ['*']}

install_requires = \
['Pygments>=2.10.0,<3.0.0',
 'attrs>=21.2.0,<22.0.0',
 'colorama>=0.4.4,<0.5.0',
 'more-itertools>=8.8.0,<9.0.0']

setup_kwargs = {
    'name': 'snakeboost',
    'version': '0.3.0',
    'description': 'Utility functions to turbocharge your snakemake workflows. Virtualenvs, tarfiles, and more.',
    'long_description': '# Snakeboost\n\nSnakeboost provides enhancers and helpers to turbocharge your [snakemake](https://snakemake.readthedocs.io/en/stable/) workflows.\nThe project is currently in it\'s alpha stage.\n\n[Full Documentation](https://snakeboost.readthedocs.io)\n\n# Script Enhancers\n\n## Overview\n\nScript enhancer functions wrap around bash scripts given to the `shell` directive in Snakemake Rules.\nAll enhancers have a common interface designed for easy use in your workflow.\nTo illustrate, we\'ll take `PipEnv` as an example (it lets you use pip virtual environments!).\n\n1. Initiate the enhancer\n\nImport the enhancer at the top of your `Snakefile` and instantiate it.\nMost enhancers take a few arguments defining their global settings.\n\n```python\nfrom snakeboost import PipEnv\n\nmy_env = PipEnv(packages=["numpy", "flake8"], root=("/tmp"))\n```\n\n2. Use the enhancer in a rule\n\nWhen instantiated, enhancers can be called using the bash command as an argument.\n\n```python\nrule lint_python:\n    inputs: "some-script.py"\n    shell:\n        my_env.script("flake8 {input}")\n```\n\nSome enhancers, such as `PipEnv`, provide multiple functions (e.g. `.script`, `.python`, etc) that provide slightly different functionality.\nOthers, such as `Tar`, have methods that return a modified instance.\n\n```python\nrule inspect_tarball:\n    inputs: "some_archive.tar.gz"\n    shell:\n        tar.using(inputs=["{input}"])("ls {input}/")\n```\n\nSnakeboost uses this slightly convoluted way of setting arguments to allow easy chaining of multiple enhancers.\nThis leads us to step 3:\n\n3. Use `boost()` to chain multiple enhancers\n\nChaining many enhancers together can quickly lead to indentation hell:\n\n```python\nrule lint_tarred_scripts:\n    inputs: "script_archive.tar.gz"\n    shell:\n        xvfb-run(\n            tar.using(inputs=["{input}"])(\n                my_env.script(\n                    "flake8 {input}/script.py"\n                )\n            )\n        )\n```\n\nThe `boost()` function lets you rewrite this as:\n\n```python\nfrom snakeboost import Boost\n\nboost = Boost()\n\nrule lint_tarred_scripts:\n    inputs: "script_archive.tar.gz"\n    shell:\n        boost(\n            xvfb_run,\n            tar.using(inputs=["{input}"]),\n            my_env.script,\n            "flake8 {input}/script.py"\n        )\n```\n\nThat makes your rules much cleaner!\nHowever, boost provides a much more important function, as discussed fully in the [docs...](https://snakeboost.readthedocs.io/boost.html)\n\n\n## Enhancers\n\nCurrent enhancers include:\n\n* `PipEnv`: Use pip environments in snakemake workflows\n* `PyScript`: Use python scripts along with pip envs and other Snakeboost enhancers\n* `Tar`: tar up your output files or untar input files before the job\n* `Xvfb`: Start a virtual X-server to run headless graphical commands (e.g. rendering) on servers without graphics support.\n\n# Contributing\n\nIf you have a small utility function for your Snakemake workflows, it would likely make a great addition to the Snakeboost ecosystem.\nScript enhancers should follow the basic interface of the other enhancers: a class initialized with global settings that exposes one or more functions that take a bash script as argument.\n\nSnakebids uses [Poetry](https://python-poetry.org/) for dependency management and [pre-commit](https://pre-commit.com/) for Quality Assurance tests.\nIf Poetry is not already installed on your system, follow the [instructions](https://python-poetry.org/docs/master/) on their website.\nThen clone the repo and initialize by running:\n\n```bash\npoetry install\npoetry run pre-commit install\n```\n',
    'author': 'Peter Van Dyken',
    'author_email': 'pvandyk2@uwo.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
