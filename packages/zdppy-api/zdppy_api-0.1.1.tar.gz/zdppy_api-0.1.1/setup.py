# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zdppy_api',
 'zdppy_api.anyio',
 'zdppy_api.anyio._backends',
 'zdppy_api.anyio._core',
 'zdppy_api.anyio.abc',
 'zdppy_api.anyio.streams',
 'zdppy_api.dependencies',
 'zdppy_api.middleware',
 'zdppy_api.multipart',
 'zdppy_api.openapi',
 'zdppy_api.security',
 'zdppy_api.sniffio',
 'zdppy_api.starlette',
 'zdppy_api.starlette.middleware']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=3.6.1,<4.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'python-multipart>=0.0.5,<0.0.6',
 'uvicorn>=0.17.6,<0.18.0']

setup_kwargs = {
    'name': 'zdppy-api',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'zhangdapeng520',
    'author_email': 'pygosuperman@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
