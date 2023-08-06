# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['gh_webhooks']

package_data = \
{'': ['*']}

install_requires = \
['pydantic[email]==1.9.0',
 'stringcase>=1.2.0,<2.0.0',
 'typing-extensions>=4.2.0,<5.0.0']

setup_kwargs = {
    'name': 'gh-webhooks',
    'version': '0.6.0',
    'description': 'Typed event handling for GitHub Webhooks',
    'long_description': '# Typed event handling for GitHub Webhooks\n\n[![CI](https://github.com/k2bd/gh-webhooks/actions/workflows/ci.yml/badge.svg)](https://github.com/k2bd/gh-webhooks/actions/workflows/ci.yml)\n[![codecov](https://codecov.io/gh/k2bd/gh-webhooks/branch/main/graph/badge.svg?token=NE813K6GET)](https://codecov.io/gh/k2bd/gh-webhooks)\n[![PyPI](https://img.shields.io/pypi/v/gh-webhooks)](https://pypi.org/project/gh-webhooks/)\n\nThis library provides types for using GitHub Webhook events in Python, and a class for registering event handlers for each event type.\n\nAn example using FastAPI:\n\n```python\nfrom fastapi import FastAPI, Request\nfrom gh_webhooks import GhWebhookEventHandler\nfrom gh_webhooks.types import BranchProtectionRuleCreated\n\napp = FastAPI()\nevent_handler = GhWebhookEventHandler()\n\n@event_handler.on(BranchProtectionRuleCreated)\nasync def handle_new_branch_protection_rule(event: BranchProtectionRuleCreated):\n    print(event.repository.name)\n\n\n@app.post("/payload")\nasync def handle_webhook_payload(request: Request):\n    event = await request.json()\n    await event_handler.handle_event(event)\n```\n\nYou can also see a basic example project [here](https://github.com/k2bd/gh-webhooks-test).\n\nMultiple handlers can be registered to the same event type, and they\'ll run concurrently.\n\nThe types are auto-generated using [datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator).\nA GitHub action maintains these types automatically.\n\nIntegration tests are also auto-generated from the [example events](https://github.com/octokit/webhooks/tree/master/payload-examples) in the GitHub Webhook events spec docs.\n\n## Developing\n\nInstall [Poetry](https://python-poetry.org/) and `poetry install` the project\n\n### Useful Commands\n\nNote: if Poetry is managing a virtual environment for you, you may need to use `poetry run poe` instead of `poe`\n\n- `poe autoformat` - Autoformat code\n- `poe lint` - Lint code\n- `poe test` - Run tests\n- `poe docs` - Build docs\n- `poe codegen` - Generate types\n\n### Release\n\nRelease a new version by manually running the release action on GitHub with a \'major\', \'minor\', or \'patch\' version bump selected.\nThis will create and push a new semver tag of the format `v1.2.3`, which in turn will trigger an action to automatically publish a new version to PyPI.\n\nOptionally create a release from this new tag to let users know what changed.\n',
    'author': 'Kevin Duff',
    'author_email': 'kevinkelduff@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/k2bd/gh-webhooks',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
