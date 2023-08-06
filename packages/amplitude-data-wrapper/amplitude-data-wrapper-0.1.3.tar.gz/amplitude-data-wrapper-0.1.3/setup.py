# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['amplitude_data_wrapper']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0', 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'amplitude-data-wrapper',
    'version': '0.1.3',
    'description': 'python wrapper for using the amplitude analytics and taxonomy APIs',
    'long_description': '# Amplitude analytics\n\nThis is a wrapper for Amplitude APIs. You can use it to query and export data from your account and use the taxonomy API.\n\n**Why use this package instead of other wrappers?**\n\nThis package supports regions and so you can use it with Amplitude accounts in the EU and USA.\n\nThis package also supports using a proxy so you can keep your project API keys and API secrets confidential.\n\n**Get existing chart**\n\n```python\nfrom amplitude_data_wrapper import get_chart\n\nproxies = {"http": "http://myproxy.domain.org/path"}\nr = get_chart(chart_id, api_key, api_secret, region=1, proxy=proxies)\nr.status_code  # 200\nr.text # print data\n```\n\n**Get a cohort**\n\n```python\nproxies = {"http": "http://myproxy.domain.org/path"}\nfile_path = "path-to/cohortdata.csv"\nkull = get_cohort(\n    api_key,\n    api_secret,\n    cohort_id,\n    filename=file_path,\n    props=1,\n    region=1,\n    proxy=proxies,\n)\n```\n\n**Export project data**\n\n```python\nstart = "20220601T00"\nend = "20220601T01"\ndata = export_project_data(\n    start=start,\n    end=end,\n    api_key=api_key,\n    secret=api_secret,\n    filename="path-to/projectdata_eu.zip",\n    region=1,\n)\n```',
    'author': 'Tobias McVey',
    'author_email': 'tobias.mcvey@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
