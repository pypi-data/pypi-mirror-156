# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asyncio_redis_rate_limit']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=3.10']

extras_require = \
{'aioredis': ['aioredis>=2.0'],
 'dev': ['redis>=4.3', 'aioredis>=2.0'],
 'redis': ['redis>=4.3']}

setup_kwargs = {
    'name': 'asyncio-redis-rate-limit',
    'version': '0.2.0',
    'description': 'Rate limiter for async functions using Redis as a backend',
    'long_description': "# asyncio-redis-rate-limit\n\n[![wemake.services](https://img.shields.io/badge/%20-wemake.services-green.svg?label=%20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](https://wemake-services.github.io)\n[![Build Status](https://github.com/wemake-services/asyncio-redis-rate-limit/workflows/test/badge.svg?branch=master&event=push)](https://github.com/wemake-services/asyncio-redis-rate-limit/actions?query=workflow%3Atest)\n[![codecov](https://codecov.io/gh/wemake-services/asyncio-redis-rate-limit/branch/master/graph/badge.svg)](https://codecov.io/gh/wemake-services/asyncio-redis-rate-limit)\n[![Python Version](https://img.shields.io/pypi/pyversions/asyncio-redis-rate-limit.svg)](https://pypi.org/project/asyncio-redis-rate-limit/)\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n\nRate limiter for async functions using Redis as a backend.\n\n\n## Features\n\n- Small and simple\n- Can be used as a decorator or as a context manager\n- Can be used for both clients and servers\n- Works with `asyncio`\n- Works with any amount of processes\n- Works with both [`redis.asyncio.client.Redis`](https://redis-py.readthedocs.io/en/stable/examples/asyncio_examples.html) and [`aioredis`](https://github.com/aio-libs/aioredis-py)\n- Free of race-conditions (hopefully!)\n- Fully typed with annotations and checked with mypy, [PEP561 compatible](https://www.python.org/dev/peps/pep-0561/)\n\n\n## Installation\n\n```bash\npip install asyncio-redis-rate-limit\n```\n\nExtras available:\n- `pip install asyncio-redis-rate-limit[redis]`\n- `pip install asyncio-redis-rate-limit[aioredis]`\n\n\n## Example\n\nAs a decorator:\n\n```python\n>>> from asyncio_redis_rate_limit import rate_limit, RateSpec\n>>> from redis.asyncio import Redis as AsyncRedis  # pip install redis\n\n>>> redis = AsyncRedis.from_url('redis://localhost:6379')\n\n>>> @rate_limit(\n...    rate_spec=RateSpec(requests=1200, seconds=60),\n...    backend=redis,\n... )\n... async def request() -> ...:\n...     ...   # Do something useful! Call this function as usual.\n\n```\n\nOr as a context manager:\n\n```python\n>>> from asyncio_redis_rate_limit import RateLimiter, RateSpec\n>>> from redis.asyncio import Redis as AsyncRedis  # pip install redis\n\n>>> redis = AsyncRedis.from_url('redis://localhost:6379')\n\n>>> async def request() -> ...:\n...     async with RateLimiter(\n...         unique_key='api-name.com',\n...         backend=redis,\n...         rate_spec=RateSpec(requests=5, seconds=1),\n...     ):\n...         ...  # Do the request itself.\n\n```\n\n\n## License\n\n[MIT](https://github.com/wemake-services/asyncio-redis-rate-limit/blob/master/LICENSE)\n\n\n## Credits\n\nThis project was generated with [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package). Current template version is: [1d63652fbb33ebe2f6d932f511b7f529a4ce2d2a](https://github.com/wemake-services/wemake-python-package/tree/1d63652fbb33ebe2f6d932f511b7f529a4ce2d2a). See what is [updated](https://github.com/wemake-services/wemake-python-package/compare/1d63652fbb33ebe2f6d932f511b7f529a4ce2d2a...master) since then.\n",
    'author': 'Nikita Sobolev',
    'author_email': 'mail@sobolevn.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wemake-services/asyncio-redis-rate-limit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
