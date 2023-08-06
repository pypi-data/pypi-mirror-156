# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mongometer']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'dnspython>=2.2.1,<3.0.0',
 'pymongo>=4.1.1,<5.0.0',
 'rich>=12.4.4,<13.0.0']

entry_points = \
{'console_scripts': ['mongometer = mongometer.executor:measure']}

setup_kwargs = {
    'name': 'mongometer',
    'version': '0.1.0',
    'description': 'MongoDB aggregation pipeline performance checker',
    'long_description': '## MongoMeter\n\nMongoDB aggregation pipeline performance checker\n\n### Install\n\n```shell\npip install mongometer\n```\n\n### Console\n\n#### Example\n\nInput\n\n```shell\nmongometer --url="mongodb://test:test@localhost:27017" --db=shop --collection bikes --path agg.json\n```\n\nOutput\n\n```shell\nProcessing ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00\n$match     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00\n$set       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00\n$match     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00\n$lookup    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00\n$unwind    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00\n$unwind    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00\n$project   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00\n$sort      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00\n$facet     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00\n$set       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00\n                 Results                  \n┏━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃    ┃ Name     ┃ Time (seconds)         ┃\n┡━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩\n│ 1  │ $match   │ 1.5710415840148926     │\n│ 2  │ $set     │ 0.0                    │\n│ 3  │ $match   │ 0.0                    │\n│ 4  │ $lookup  │ 0.00015425682067871094 │\n│ 5  │ $unwind  │ 0.0014383792877197266  │\n│ 6  │ $unwind  │ 0.003248453140258789   │\n│ 7  │ $project │ 0.06569337844848633    │\n│ 8  │ $sort    │ 3.276400566101074      │\n│ 9  │ $facet   │ 0.5028722286224365     │\n│ 10 │ $set     │ 0.0                    │\n└────┴──────────┴────────────────────────┘\n\n```\n\n#### Parameters\n\n```shell\nUsage: mongometer [OPTIONS]\n\nOptions:\n  --url TEXT         MongoDB connection string  [required]\n  --db TEXT          MongoDB database name  [required]\n  --collection TEXT  MongoDB collection name  [required]\n  --path TEXT        Path to the aggregation pipeline json file  [required]\n  --repeat INTEGER   Number of repeats\n  --help             Show this message and exit.\n\n```\n\n### Python code\n\n```python\nfrom mongometer import AggregationChecker\n\nURI = "mongodb://test:test@localhost:27017"\nDB_NAME = "shop"\nCOLLECTION_NAME = "bikes"\n\nPIPELINE = [\n    {\n        "$match": {\n            "$text": {"$search": "John"},\n        }\n    },\n    {\n        "$sort": {\n            "created_at": 1\n        }\n    }\n]\n\nchecker = AggregationChecker(URI, DB_NAME, COLLECTION_NAME)\nchecker.measure(pipeline=PIPELINE).print()\n```',
    'author': 'Roman',
    'author_email': 'roman-right@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/roman-right/mongometer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
