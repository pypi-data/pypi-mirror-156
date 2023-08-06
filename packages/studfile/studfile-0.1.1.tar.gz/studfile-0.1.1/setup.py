# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['studfile']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'calligraphy-scripting==1.1.2']

entry_points = \
{'console_scripts': ['stud = studfile.main:main']}

setup_kwargs = {
    'name': 'studfile',
    'version': '0.1.1',
    'description': 'A simplified tool for making easy-to-use build scripts',
    'long_description': '# Stud\n\n## Example Studfile.yaml\n\n```yaml\n.variables:\n  all_services:\n    - foo\n    - bar\n    - baz\nbuild-docker: \n  help: "Build and optionally push docker images"\n  options:\n    - name: -s,--services\n      default: all\n      nargs: \'+\'\n      required: true\n    - name: -p,--push\n      action: store_true\n  cmd: |\n    if \'all\' in services:\n      services = all_services\n\n    for service in services:\n      docker build -t {service} -f src/{service}/Dockerfile .\n      if push:\n        docker push {service}\nbuild-local: \n  help: "Build local versions of services"\n  options:\n    - name: -s,--services\n      default: all\n      nargs: \'+\'\n      required: true\n  cmd: |\n    # notice that the all_services variable is available \n    if \'all\' in services:\n      services = all_services\n\n    for service in services:\n      # do build things here\n```\n',
    'author': 'John Carter',
    'author_email': 'jfcarter2358@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jfcarter2358/stud',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
