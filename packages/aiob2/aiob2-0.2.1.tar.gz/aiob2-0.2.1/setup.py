# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiob2']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'aiob2',
    'version': '0.2.1',
    'description': "A simple and easy to use async wrapper for Backblaze's B2 bucket API.",
    'long_description': '# aiob2\n\n---\n\n<p align="center">\n  <a href="https://www.python.org/downloads/">\n    <img alt="Python Version" src="https://img.shields.io/badge/python-3.8.10-blue.svg?color=3776AB&style=for-the-badge">\n  </a>\n  <a href="https://pypi.org/project/aiob2/">\n     <img src="https://img.shields.io/pypi/v/aiob2?color=8BC34A&style=for-the-badge" alt="PyPi">\n  </a>\n  <a href="https://opensource.org/licenses/MIT">\n     <img src="https://img.shields.io/pypi/l/aiob2?color=C0C0C0&style=for-the-badge" alt="License">\n  </a>\n</p>\n\naiob2 is an asynchronous API wrapper for the [Backblaze B2 Bucket API](https://www.backblaze.com/b2/docs/calling.html).\n\nIt will allow you to interact with your B2 bucket, it\'s files and anything else that the B2 API allows in a modern, object-oriented fashion.\n\n__**NOTE:**__ This API wrapper is by no means *complete* and has many endpoints to cover, though the main ones have been covered (they will be listed below)\n\n# Installation\n\n---\n\naiob2 is compatible with Python 3.8.10+ (this is an estimate). To install aiob2, run the following command in your (virtual) environment.\n```\npip install aiob2\n```\nAlternatively, for the latest though least stable version, you can download it from the GitHub repo:\n```\npip install git+https://github.com/Void-ux/aiob2.git\n```\n\n# Usage\n\n### Uploading\n```python\nimport aiohttp\nimport asyncio\n\nfrom aiob2 import B2ConnectionInfo, bucket\n\n# Construct our connection info\nconn_info = B2ConnectionInfo(\'key_id\', \'app_id\')\n\n# Our image to upload to our bucket\nwith open(r\'C:\\Users\\MS1\\Pictures\\Camera Roll\\IMG_5316.jpeg\', \'rb\') as file:\n    data = file.read()\n\nasync def main():\n    async with aiohttp.ClientSession() as s:\n        await bucket.upload_file(\n            content_bytes=data,\n            content_type=\'image/jpeg\',\n            file_name=\'home.jpeg\',\n            session=s,\n            bucket_id=\'bucket_id\',\n            connection_info=conn_info\n        )\n\n\nif __name__ == \'__main__\':\n    asyncio.run(main())\n```\n\nAnd that\'s it! `upload_file()` returns a `File` object that neatly wraps everything Backblaze\'s API has provided us with. The `File` object has the following **attributes**:\n```\n- account_id: str\n- action: str\n- bucket_id: str\n- content_length: int\n- content_sha1: str\n- content_md5: str\n- content_type: str\n- file_id: str\n- file_info: dict\n- file_name: str\n- file_retention: dict\n- legal_hold: dict\n- server_side_encryption: dict\n- upload_timestamp: datetime.datetime\n```\nYou can visit the [bucket.py](https://github.com/Void-ux/aiob2/aiob2/bucket.py#L20-L66) file to view the source code of this class.\n\n### Deleting\n\n```python\n# We can remove the boilerplate code and get straight to the method\nfrom aiob2 import bucket\n\nawait bucket.delete_file(\n    file_name=\'home.jpeg\',\n    file_id=\'4_z275c6d8d808e543872cc0215_f11088ad8814ee120_d20220514_m211709_c002_v0001096_t0019_u01652563029709\',\n    connection_info=conn_info,\n    session=s\n)\n```\nThis will return a `DeletedFile` object, it has the following **attributes**:\n```\n- file_name: str\n- file_id: str\n```\n\n\n### Downloading\nDownloading a file can be done either with the `name` or the `id` of it.\n\n```python\n# We can remove the boilerplate code and get straight to the method\nfrom aiob2 import bucket\n\nawait bucket.download_file_by_name(\n    file_name=\'home.jpeg\',\n    bucket_name=\'foo\',\n    connection_info=conn_info,\n    session=s\n)\n```\n\n```python\nfrom aiob2 import bucket\n\nawait bucket.download_file_by_id(\n    file_id=\'home.jpeg\',\n    connection_info=conn_info,\n    session=s\n)\n```\nThis will return a `DownloadedFile` object with the following attributes:\n```\n- file_name: str\n- file_id: str\n- content_sha1: str\n- upload_timestamp: datetime.datetime\n- accept_ranges: str\n- content: bytes\n- content_type: str\n- content_length: str\n- date: str\n```\n**NOTE:** There are many kwargs you can provide when downloading a file, it\'s recommended to take a look at the source \ncode to see if any can benefit you and your usecase.\n\n# License\n\n---\n\nThis project is released under the [MIT License](https://opensource.org/licenses/MIT).',
    'author': 'Dan',
    'author_email': 'the.void.altacc@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
