# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['redisconfig']

package_data = \
{'': ['*']}

install_requires = \
['redis>=3,<5']

extras_require = \
{':python_version == "3.6"': ['dataclasses>=0.8,<0.9'],
 'dev': ['pytest>=6.2.5,<7.0.0',
         'black==22.3.0',
         'mypy>=0.920,<0.921',
         'flake8>=4.0.1,<5.0.0'],
 'test': ['pytest>=6.2.5,<7.0.0',
          'black==22.3.0',
          'mypy>=0.920,<0.921',
          'flake8>=4.0.1,<5.0.0']}

setup_kwargs = {
    'name': 'redisconfig',
    'version': '0.1.1',
    'description': 'Simple, robust Redis configuration for Python',
    'long_description': "# redisconfig\n\nSimple, robust Redis configuration for Python\n\n## Installation\n\n```\npip install redisconfig\n```\n\n## Basic Usage\n\n```\n>>> import redisconfig\n\n>>> config = redisconfig.RedisConfig()\nRedisConfig(host='127.0.0.1', port=6379, db=0, ssl=False, password=None)\n\n>>> config.host\n'127.0.0.1'\n\n>>> config.url()\n'redis://127.0.0.1:6379/0'\n\n>>> config.connection()\nRedis<ConnectionPool<Connection<host=127.0.0.1,port=6379,db=0>>>\n```\n\n### REDIS_URL Environment Variable\n\nIn many cases the Redis connection URL is stored in the REDIS_URL environment variable. redisconfig will use that value as a default for several operations, such as the module-level config() and connection() methods. With an environment variable of `REDIS_URL=rediss://noop:badpassword@10.0.0.1/2`:\n\n```\n>>> redisconfig.config()\nRedisConfig(host='10.0.0.1', port=6379, db=2, ssl=True, password='badpassword')\n\n>>> redisconfig.connection()\nRedis<ConnectionPool<SSLConnection<host=10.0.0.1,port=6379,db=2>>>\n```\n\n### Update Configuration Values\n\nYou can update values directly like `config.db = 5` but sometimes you want to change values without changing the underlying configuration. The url() and replace() methods on RedisConfig allow you to make new urls or configs without changing the original values.\n\nCreate a new URL:\n\n```\n>>> config = redisconfig.RedisConfig()\n>>> config.url()\n'redis://127.0.0.1:6379/0'\n\n>>> config.url(db=2)\n'redis://127.0.0.1:6379/2'\n```\n\nCreate a new RedisConfig instance:\n\n```\n>>> config.replace(db='10.0.0.1')\nRedisConfig(host='10.0.0.1', port=6379, db=0, ssl=False, password=None)\n```\n\n## Developing\n\nThe following things are needed to use this repository:\n\n-   [Git](https://git-scm.com)\n-   [Python 3.6.2+](https://www.python.org/downloads/)\n-   [Poetry](https://python-poetry.org/)\n\nOnce you have the prerequisites installed and have cloned the repository you can ready your development environment with `poetry install -E dev`. You should see output similar to:\n\n```\n$ poetry install -E dev\nCreating virtualenv redisconfig in /tmp/redisconfig/.venv\nInstalling dependencies from lock file\n\n...\n\nInstalling the current project: redisconfig (0.1.1)\n```\n\n## Testing\n\n```\npoetry run pytest\n```\n\n## Changelog\n\n### 0.1.1\n\n-   Fix typing-extensions import on Python >=3.8\n\n### 0.1.0\n\n-   Initial release\n",
    'author': 'Jeremy Carbaugh',
    'author_email': 'jeremy.carbaugh@xplortechnologies.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/xplor/redisconfig',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
