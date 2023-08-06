# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['todo_extract']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'todo-extract',
    'version': '0.2.2',
    'description': 'Extract TODO items from the text file',
    'long_description': '# TODO extractor from markdown file\nPython script for extracting TODO notes from text file.\n\nList can be grouped into sections and can be summarized with stats.\n\n\n- [Requirements](#requirements)\n- [Usage](#usage)\n- [Examples](#examples)\n  - [extraction of bare list, no stats](#extraction-of-bare-list-no-stats)\n  - [extraction of list summarized with stats](#extraction-of-list-summarized-with-stats)\n  - [extraction of list divided into sections/chapters](#extraction-of-list-divided-into-sectionschapters)\n- [License](#license)\n\n\n## Installation\n```\n$ pip install todo-extract\n```\n\n## Requirements\nThe script requires Python3 installed, no other dependencies.\n\n## Usage\n```sh\n$ todo-extract --help\n```\n\n```\nusage: todo-extract [-h] [-s] [-c] file_name\n\nExtract todo items from markdown file\n\npositional arguments:\n  file_name       markdown file path\n\noptional arguments:\n  -h, --help      show this help message and exit\n  -s, --stats     display stats\n  -c, --chapters  display items grouped by important/not important and done/not done\n```\n\n## Examples\n\n### extraction of bare list, no stats\n```sh\n$ todo-extract file.md\n```\n\noutput:\n```\n- buy a bag of chips\n- buy a bag of cookies\n- buy apples\n- buy oranges\n- buy bananas\n- buy pears\n- buy plums\n- buy avocados\n- buy water \n- [!] buy bread\n```\n\n### extraction of list summarized with stats\n```sh\n$ todo-extract --stats file.md\n```\n\n```\n- buy a bag of chips\n- buy a bag of cookies\n- buy apples\n- buy oranges\n- buy bananas\n- buy pears\n- buy plums\n- buy avocados\n- buy water \n- [!] buy bread\n\nstats:\n-------\n10  all items (done or not done)\n3   not done normal items   (42%  of all normal items are not done)\n4   done normal items       (57%  of all normal items are done)\n2   important items todo    (66%  of all important items are not done)\n1   important items done    (33%  of all important items are done)\n```\n### extraction of list divided into sections/chapters\n```sh\n$ todo-extract --chapters file.md\n```\n\n```\n==== Done normal items: 4 ====\n\n- buy oranges\n- buy bananas\n- buy pears\n- buy plums\n\n==== Important done items: 1 ====\n\n- [!] buy bread\n\n==== Normal todo items: 3 ====\n\n- buy a bag of chips\n- buy a bag of cookies\n- buy apples\n\n==== Important todo items: 2 ====\n\n- buy avocados\n- buy water \n```\n## License\nMIT\n',
    'author': 'Krystian Safjan',
    'author_email': 'ksafjan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.0,<4.0',
}


setup(**setup_kwargs)
