# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['openldap_acl_test']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0']

setup_kwargs = {
    'name': 'openldap-acl-test',
    'version': '0.9.1',
    'description': 'OpenLDAP ACL check tool',
    'long_description': '.. image:: https://github.com/mypaceshun/openldap-acl-test/actions/workflows/main.yml/badge.svg\n          :target: https://github.com/mypaceshun/openldap-acl-test/actions/workflows/main.yml\n.. image:: https://codecov.io/gh/mypaceshun/openldap-acl-test/branch/main/graph/badge.svg?token=1L16BLXJ74\n           :target: https://codecov.io/gh/mypaceshun/openldap-acl-test\n.. image:: https://readthedocs.org/projects/openldap-acl-test/badge/?version=latest\n           :target: https://openldap-acl-test.readthedocs.io/ja/latest/?badge=latest\n           :alt: Documentation Status\n\nOpenLDAP ACL Test\n=================\n\nOpenLDAPのACLをチェックを補助するツールです。\n設定ファイルをよみ、適切に ``slapacl`` コマンドを実行し、\n結果を記録します。\n',
    'author': 'KAWAI Shun',
    'author_email': 'mypaceshun@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mypaceshun/openldap-acl-test',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
