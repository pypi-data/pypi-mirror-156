# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['strawberry_mage',
 'strawberry_mage.backends',
 'strawberry_mage.backends.dataloader',
 'strawberry_mage.backends.sqlalchemy',
 'strawberry_mage.core',
 'strawberry_mage.core.resolvers']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy-Utils>=0.38.2,<0.39.0',
 'SQLAlchemy[asyncio]>=1.4.25,<2.0.0',
 'aiosqlite>=0.17.0,<0.18.0',
 'frozendict>=2.0.6,<3.0.0',
 'inflection>=0.5.1,<0.6.0',
 'overrides>=6.1.0,<7.0.0',
 'strawberry-graphql>0.80.0,<1.0.0']

setup_kwargs = {
    'name': 'strawberry-graphql-mage',
    'version': '0.0.1a9.dev1656261647',
    'description': 'An automated, modular, backend-agnostic GraphQL API generator',
    'long_description': '# Strawberry-GraphQL-Mage\n\nCreates a GraphQL backend for your database with really low effort.\n\nThe mainly developed feature is currently the SQLAlchemy backend with universal dataloader support coming hopefully soon.\n\nPerformance is currently not a major factor - this is mostly a helper library to make creating GraphQL endpoints easier.\n\n## Still under heavy development\n\nFeel free to use it and create issues though.\n\nContributions are welcome as well.\n\n## Roadmap\n\n- [x] Generating a basic GraphQL schema\n- [x] Queries\n- [x] Mutations\n- [ ] Subscriptions\n- [x] Backend abstraction\n- [ ] Move used meta attributes to an isolated Metaclass of the object instead of polluting the object with them\n- [ ] SQLAlchemy backend\n  - [x] Entity models\n  - [x] Implement basic mutations/queries\n  - [x] Add basic tests\n  - [x] Filtering, ordering\n  - [x] Utility functions for relationships\n  - [ ] Nested pagination\n  - [ ] Add more tests\n  - [x] Asyncio\n  - [ ] Implement abstract sqla models\n- [ ] Strawberry Dataloader universal backend\n  - [ ] ...\n- [ ] Add more filters\n- [ ] Add options for custom data-types\n- [ ] Setup CI\n- [ ] Try some authorization / authentication\n- [ ] Write instructions for using the app\n- [ ] Write instructions for creating custom backends\n',
    'author': 'Vojtěch Dohnal',
    'author_email': 'vojdoh@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
