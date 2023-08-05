# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sparrow_datums',
 'sparrow_datums.boxes',
 'sparrow_datums.stream',
 'sparrow_datums.tracking']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.20.0,<2.0.0', 'rich>=10.14.0,<11.0.0', 'typer[all]>=0.4.0,<0.5.0']

setup_kwargs = {
    'name': 'sparrow-datums',
    'version': '0.8.1.dev1655842168',
    'description': 'A Python package for data structures',
    'long_description': '# sparrow-datums\n\n<div align="center">\n\nA Python package for data structures\n\n</div>\n\n### Poetry\n\nWant to know more about Poetry? Check [its documentation](https://python-poetry.org/docs/).\n\n<details>\n<summary>Details about Poetry</summary>\n<p>\n\nPoetry\'s [commands](https://python-poetry.org/docs/cli/#commands) are very intuitive and easy to learn, like:\n\n- `poetry add numpy@latest`\n- `poetry run pytest`\n- `poetry publish --build`\n\netc\n</p>\n</details>\n\n## Building and releasing your package\n\nBuilding a new version of the application contains steps:\n\n- Bump the version of your package `poetry version <version>`. You can pass the new version explicitly, or a rule such as `major`, `minor`, or `patch`. For more details, refer to the [Semantic Versions](https://semver.org/) standard.\n- Make a commit to `GitHub`.\n- Create a `GitHub release`.\n- And... publish 🙂 `poetry publish --build`\n\n\n## Installation\n\n```bash\npip install -U sparrow-datums\n```\n\nor install with `Poetry`\n\n```bash\npoetry add sparrow-datums\n```\n\nThen you can run\n\n```bash\nsparrow-datums --help\n```\n\nor with `Poetry`:\n\n```bash\npoetry run sparrow-datums --help\n```\n\n### Makefile usage\n\n[`Makefile`](https://github.com/sparrowml/sparrow-datums/blob/master/Makefile) contains a lot of functions for faster development.\n\n<details>\n<summary>1. Download and remove Poetry</summary>\n<p>\n\nTo download and install Poetry run:\n\n```bash\nmake poetry-download\n```\n\nTo uninstall\n\n```bash\nmake poetry-remove\n```\n\n</p>\n</details>\n\n<details>\n<summary>2. Install all dependencies and pre-commit hooks</summary>\n<p>\n\nInstall requirements:\n\n```bash\nmake install\n```\n\nPre-commit hooks coulb be installed after `git init` via\n\n```bash\nmake pre-commit-install\n```\n\n</p>\n</details>\n\n<details>\n<summary>3. Codestyle</summary>\n<p>\n\nAutomatic formatting uses `pyupgrade`, `isort` and `black`.\n\n```bash\nmake codestyle\n\n# or use synonym\nmake formatting\n```\n\nCodestyle checks only, without rewriting files:\n\n```bash\nmake check-codestyle\n```\n\n> Note: `check-codestyle` uses `isort`, `black` and `darglint` library\n\nUpdate all dev libraries to the latest version using one comand\n\n```bash\nmake update-dev-deps\n```\n\n<details>\n<summary>4. Code security</summary>\n<p>\n\n```bash\nmake check-safety\n```\n\nThis command launches `Poetry` integrity checks as well as identifies security issues with `Safety` and `Bandit`.\n\n```bash\nmake check-safety\n```\n\n</p>\n</details>\n\n</p>\n</details>\n\n<details>\n<summary>5. Type checks</summary>\n<p>\n\nRun `mypy` static type checker\n\n```bash\nmake mypy\n```\n\n</p>\n</details>\n\n<details>\n<summary>6. Tests with coverage badges</summary>\n<p>\n\nRun `pytest`\n\n```bash\nmake test\n```\n\n</p>\n</details>\n\n<details>\n<summary>7. All linters</summary>\n<p>\n\nOf course there is a command to ~~rule~~ run all linters in one:\n\n```bash\nmake lint\n```\n\nthe same as:\n\n```bash\nmake test && make check-codestyle && make mypy && make check-safety\n```\n\n</p>\n</details>\n\n<details>\n<summary>8. Docker</summary>\n<p>\n\n```bash\nmake docker-build\n```\n\nwhich is equivalent to:\n\n```bash\nmake docker-build VERSION=latest\n```\n\nRemove docker image with\n\n```bash\nmake docker-remove\n```\n\nMore information [about docker](https://github.com/sparrowml/sparrow-datums/tree/master/docker).\n\n</p>\n</details>\n\n<details>\n<summary>9. Cleanup</summary>\n<p>\nDelete pycache files\n\n```bash\nmake pycache-remove\n```\n\nRemove package build\n\n```bash\nmake build-remove\n```\n\nDelete .DS_STORE files\n\n```bash\nmake dsstore-remove\n```\n\nRemove .mypycache\n\n```bash\nmake mypycache-remove\n```\n\nOr to remove all above run:\n\n```bash\nmake cleanup\n```\n\n</p>\n</details>\n',
    'author': 'Sparrow Computing',
    'author_email': 'ben@sparrow.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sparrowml/sparrow-datums',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
