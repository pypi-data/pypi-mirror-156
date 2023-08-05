# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydantic_ssm_settings']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.21.45,<2.0.0', 'pydantic>=1.6.2,<2.0.0']

setup_kwargs = {
    'name': 'pydantic-ssm-settings',
    'version': '0.2.2',
    'description': "Replace Pydantic's builtin Secret Support with a configuration provider that loads parameters from AWS Systems Manager Parameter Store.",
    'long_description': "# pydantic-ssm-settings\n\nReplace Pydantic's builtin [Secret Support](https://pydantic-docs.helpmanual.io/usage/settings/#secret-support) with a configuration provider that loads parameters from [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html). Parameters are loaded _lazily_, meaning that they are only requested from AWS if they are not provided via [standard field value priority](https://pydantic-docs.helpmanual.io/usage/settings/#field-value-priority) (i.e. initialiser, environment variable, or via `.env` file).\n\n## Usage\n\nThe simplest way to use this module is to inhert your settings `Config` class from `AwsSsmSourceConfig`. This will overwrite the [`file_secret_settings` settings source](https://pydantic-docs.helpmanual.io/usage/settings/#customise-settings-sources) with the `AwsSsmSettingsSource`. Provide a prefix to SSM parameters via the `_secrets_dir` initialiser value or the `secrets_dir` Config value.\n\n```py\nfrom pydantic import BaseSettings\nfrom pydantic_ssm_settings import AwsSsmSourceConfig\n\n\nclass WebserviceSettings(BaseSettings):\n    some_val: str\n    another_val: int\n\n    class Config(AwsSsmSourceConfig):\n        ...\n\nSimpleSettings(_secrets_dir='/prod/webservice')\n```\n\nThe above example will attempt to retreive values from `/prod/webservice/some_val` and `/prod/webservice/another_val` if not provided otherwise.",
    'author': 'Anthony Lukach',
    'author_email': 'anthonylukach@gmail.com',
    'maintainer': 'Anthony Lukach',
    'maintainer_email': 'anthonylukach@gmail.com',
    'url': 'https://github.com/developmentseed/pydantic-ssm-settings/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
