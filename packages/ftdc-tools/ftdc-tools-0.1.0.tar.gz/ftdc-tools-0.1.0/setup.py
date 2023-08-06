# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ftdc_tools']

package_data = \
{'': ['*']}

install_requires = \
['aiofile>=3.7.4,<4.0.0',
 'black>=22.3.0,<23.0.0',
 'flake8-annotations>=2.9.0,<3.0.0',
 'flake8-bandit>=3.0.0,<4.0.0',
 'flake8-bugbear>=22.4.25,<23.0.0',
 'flake8-docstrings>=1.6.0,<2.0.0',
 'flake8-isort>=4.1.1,<5.0.0',
 'flake8>=4.0.1,<5.0.0',
 'mypy>=0.960,<0.961',
 'pytest-asyncio>=0.18.3,<0.19.0',
 'pytest-flake8>=1.1.1,<2.0.0',
 'pytest-mypy>=0.9.1,<0.10.0']

setup_kwargs = {
    'name': 'ftdc-tools',
    'version': '0.1.0',
    'description': 'Pure python package that provides tools required to decode and process FTDC data.',
    'long_description': '# ftdc-tools - Pure Python package for FTDC\nThis package provides tools required to decode and process FTDC data. So whats unique about this package\n\n* This a pure python package and does not rely on any external binaries for decoding FTDC data.\n* This package provides streaming support. With this feature the whole FTDC files is not loaded in memory and is capable of processing large FTDC file.\n* Async support for faster processing.\n\n## Getting Started - Users\n```\npip install ftdc-tools\n```\n\n## Usage\n\n### Decoding FTDC file from URL - Streaming approach\n```\nfrom ftdc_tools.ftdc_decoder import FTDC\nimport requests\nurl = "https://genny-metrics.s3.amazonaws.com/performance_linux_wt_repl_genny_scale_InsertRemove_patch_b2098c676bdc64e3194734fa632b133c47496646_61f955933066150fca890e4a_22_02_01_15_58_36_0/canary_InsertRemove.ActorFinished"\n\n# Streaming FTDC data\nresponse = requests.get(url, stream=True)\nfor ftdc_row in FTDC(response.raw):\n    print(ftdc_row)\n```\n\n### Decoding FTDC file from URL - Non-streaming approach\n```\nfrom ftdc_tools.ftdc_decoder import FTDC\nimport requests\nurl = "https://genny-metrics.s3.amazonaws.com/performance_linux_wt_repl_genny_scale_InsertRemove_patch_b2098c676bdc64e3194734fa632b133c47496646_61f955933066150fca890e4a_22_02_01_15_58_36_0/canary_InsertRemove.ActorFinished"\n\nresponse = requests.get(url)\nfor ftdc_row in FTDC(response.content):\n    print(ftdc_row)\n```\n\n### Decoding FTDC file from URL - Aysnc streaming approach\n```\nimport asyncio\nimport aiohttp\nfrom ftdc_tools.ftdc_decoder import FTDC\nurl = "https://genny-metrics.s3.amazonaws.com/performance_linux_wt_repl_genny_scale_InsertRemove_patch_b2098c676bdc64e3194734fa632b133c47496646_61f955933066150fca890e4a_22_02_01_15_58_36_0/canary_InsertRemove.ActorFinished"\n\nasync def decode_ftdc():\n    async with aiohttp.ClientSession() as session:\n        async with session.get(url) as resp:\n            async for x in FTDC(resp.content.iter_chunked(10000)):\n                print(x)\n\n\nasyncio.run(decode_ftdc())\n```\n\n### Decoding FTDC file from URL - Using all the available memory.\nOne of the disadvantages of using a streaming approach is that it\'s slow compared to in-memory processing.\nTo optimize memory usage and achieve the best performance for available memory, users can pass the memory option to the FTDC class.\nWhen combined with an async streaming approach, users should achieve the best possible performance with available memory.\n```\nimport asyncio\nimport aiohttp\nfrom ftdc_tools.ftdc_decoder import FTDC\nurl = "https://genny-metrics.s3.amazonaws.com/performance_linux_wt_repl_genny_scale_InsertRemove_patch_b2098c676bdc64e3194734fa632b133c47496646_61f955933066150fca890e4a_22_02_01_15_58_36_0/canary_InsertRemove.ActorFinished"\n\nasync def decode_ftdc():\n    async with aiohttp.ClientSession() as session:\n        async with session.get(url) as resp:\n            async for x in FTDC(resp.content.iter_chunked(10000), memory=10000*1000):\n                print(x)\n\n\nasyncio.run(decode_ftdc())\n```\n\n## Getting Started - Developers\n\nGetting the code:\n```\n$ git clone git@github.com:mongodb/ftdc-tools.git\n$ cd ftdc-tools\n```\n\nInstallation\n\n```\n$ pip install poetry\n$ poetry install\n```\n\nTesting/linting:\n```\n$ poetry run black ftdc_tools tests\n$ poetry run isort ftdc_tools tests\n$ poetry run pytest\n$ poetry run flake8\n```\n',
    'author': 'Mridul Augustine',
    'author_email': 'mridul.augustine@mongodb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mongodb/ftdc-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
