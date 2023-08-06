# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['git_ripper', 'git_ripper.utils']

package_data = \
{'': ['*']}

install_requires = \
['aiodns>=3.0.0,<4.0.0', 'aiohttp>=3.8.1,<4.0.0', 'cchardet>=2.1.7,<3.0.0']

entry_points = \
{'console_scripts': ['git-ripper = git_ripper.cli:main']}

setup_kwargs = {
    'name': 'git-ripper',
    'version': '0.2.2',
    'description': 'Downloads git repos from the web.',
    'long_description': "# Git Ripper ⚰️\n\n![image](https://user-images.githubusercontent.com/12753171/174469279-fee0d9d5-7990-4237-8692-d7d5b7be86e5.png)\n\nDownloads git repos from the web.\n\nFrom Russia with hate, szuki! Developed by secret KGB konstruktor buyro by red soviet communits hackers. Enjoy before you die in nuclear war...\n\n![image](https://user-images.githubusercontent.com/12753171/174526255-6c9d8834-8247-48ad-a263-c2255e292223.png)\n\nDownloading git repo from ukrainian neonazi site.\n\nFeatures:\n\n- Asynchronous and fast.\n- Mass git downloading.\n- Unix-friendly for geeks.\n- Colored output for gay people and transformers.\n- Powered by Putin's 🇷🇺 dark energy.\n- Use Python programming language instead peaces of shit like Go or Rust. You can easily customize it!\n\n```bash\n# install\n$ pipx install git-ripper\n\n$ git-ripper https://<target>\n\n# so...\n$ git-ripper < urls.txt\n$ command | git-ripper\n\n# see help\n$ git-ripper -h\n```\n\n## How To Find Sensitive data\n\n```bash\n# extract text from git objects\nfor i in output/target/.git/objects/*/*; do\n  zlib-flate -uncompress < $i | strings >> /tmp/decoded\n\n# find passwords\n$ grep -A2 -B2 -n -i password /tmp/decoded\n```\n\n## FIXME\n\nTo stop the execution, you need to press `^C` several times.\n\n## Notes\n\nGit directory structure:\n\n![image](https://www.apriorit.com/images/articles/git_remote_helper/git_directory_entities.jpg)\n\n- [Git Object Format](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)\n\nСборка происходит автоматически при добавлении тега.\n",
    'author': 'tz4678',
    'author_email': 'tz4678@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tz4678/git-ripper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
