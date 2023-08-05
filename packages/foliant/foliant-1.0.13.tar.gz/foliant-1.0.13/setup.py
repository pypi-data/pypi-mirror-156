# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['foliant',
 'foliant.backends',
 'foliant.cli',
 'foliant.config',
 'foliant.preprocessors']

package_data = \
{'': ['*']}

install_requires = \
['cliar>=1.3.2,<2.0.0', 'prompt_toolkit>=2.0,<3.0', 'pyyaml>=5.1.1,<6.0.0']

entry_points = \
{'console_scripts': ['foliant = foliant.cli:entry_point']}

setup_kwargs = {
    'name': 'foliant',
    'version': '1.0.13',
    'description': 'Modular, Markdown-based documentation generator that makes pdf, docx, html, and more.',
    'long_description': '[![PyPI](https://img.shields.io/pypi/v/foliant.svg)](https://pypi.org/project/foliant/)\n[![Travis](https://img.shields.io/travis/foliant-docs/foliant.svg)](https://travis-ci.org/foliant-docs/foliant)\n[![codecov](https://codecov.io/gh/foliant-docs/foliant/branch/develop/graph/badge.svg)](https://codecov.io/gh/foliant-docs/foliant)\n\n![](img/foliant.gif)\n\n# Foliant\n\nFoliant is an all-in-one single-source documentation authoring tool. It lets you produce standalone documents in **pdf** and **docx**, build **static websites** and upload pages to **Confluence**, all from single Markdown source.\n\nFoliant is a higher order tool, which means it uses other programs to do its job. For building pdf and docx, it can use [Pandoc](https://pandoc.org/) or [md-to-pdf](https://github.com/simonhaenisch/md-to-pdf), for websites [MkDocs](https://www.mkdocs.org/), [Aglio](https://github.com/danielgtaylor/aglio) or [Slate](https://github.com/slatedocs/slate).\n\nFoliant preprocessors let you reuse parts of your documents, show and hide content with flags, render diagrams from text, and much more.\n\nFoliant is highly extensible, so if it lacks some functions or output formats you can always make a plugin for it or request one from our team.\n\n[Foliant Documentation](https://foliant-docs.github.io/docs/) website.\n\n## Installation\n\nFoliant is written in Python and requires Python 3.6.\n\nTo install Foliant, use pip:\n\n```shell\n$ pip install foliant\n```\n\nBackends, extensions, and preprocessors are installed with pip as well. For the Quickstart, you\'ll need the [MkDocs backend](https://github.com/foliant-docs/foliantcontrib.mkdocs) and [init CLI extension](https://github.com/foliant-docs/foliantcontrib.init):\n\n```shell\n$ pip install foliantcontrib.mkdocs foliantcontrib.init\n```\n\nTo build pdf and docx, install the [Pandoc backend](https://github.com/foliant-docs/foliantcontrib.pandoc):\n\n```shell\n$ pip install foliantcontrib.pandoc\n```\n\n\n## Quickstart\n\n1. Create a new project:\n\n```shell\n$ foliant init\nEnter the project name: Hello Foliant\n✓ Generating Foliant project\n─────────────────────\nProject "Hello Foliant" created in /path/to/hello-foliant\n```\n\nThis command creates a basic Foliant project:\n\n```\nhello-foliant/\n├── foliant.yml\n└── src\n    └── index.md\n\n1 directory, 2 files\n```\n\n`foliant.yml` is the project config file, `src` is the directory that contains the project source files (initially, just one file `index.md`).\n\n2. Build a website from the newly created project:\n\n```shell\n$ foliant make site -p hello-foliant/\n✓ Parsing config\n✓ Applying preprocessor mkdocs\n✓ Making site with MkDocs\n─────────────────────\nResult: Hello_Foliant-0.1.0-2017-11-24.mkdocs\n```\n\n3. Run a local webserver in the site directory and see the site in your browser:\n\n```shell\n$ cd Hello_Foliant-0.1.0-2017-11-24.mkdocs\n$ python -m http.server\nServing HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...\n```\n\n4. Build a standalone pdf document from the project:\n\n```shell\n$ foliant make pdf -p hello-foliant/\n✓ Parsing config\n✓ Applying preprocessor mkdocs\n✓ Making pdf with Pandoc\n─────────────────────\nResult: Hello_Foliant-0.1.0-2017-11-24.pdf\n```\n\n> **Important**\n>\n> To produce pdf, Pandoc first converts Markdown to tex and then coverts it to pdf. To convert pdf > from tex, you need to have a LaTeX distribution installed:\n>\n> -   [MacTeX](http://tug.org/mactex/) for macOS\n> -   [MikTeX](https://miktex.org/) for Windows\n> -   [TeXLive](https://tug.org/texlive/) for Linux\n',
    'author': 'Konstantin Molchanov',
    'author_email': 'moigagoo@live.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://foliant-docs.github.io/docs/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
