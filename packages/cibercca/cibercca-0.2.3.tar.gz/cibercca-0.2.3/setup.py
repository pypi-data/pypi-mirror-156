# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cibercca']

package_data = \
{'': ['*'], 'cibercca': ['inventory/*']}

install_requires = \
['PyYAML==6.0',
 'hvac==0.11.2',
 'napalm==3.3.1',
 'netmiko==3.4.0',
 'nornir==3.2.0',
 'openpyxl==3.0.9',
 'pandas==1.3.4',
 'tabulate==0.8.9',
 'tqdm==4.62.3',
 'ttp==0.8.1',
 'typer==0.4.1']

entry_points = \
{'console_scripts': ['ciberc-ca = cibercca.main:main']}

setup_kwargs = {
    'name': 'cibercca',
    'version': '0.2.3',
    'description': 'CiberC Code Automation - reports excel and json formats',
    'long_description': "# ciberc-ca\n\nCiberC Code Automation\n\nGeneration of interface reports for IOS devices in parallel, cross validations for migration of VRFs from IOS devices to XR\n\n# https://www.ciberc.com\n\n#  Technology stack\n\nPython 3.6 or higher\n\n#  Status\n\nlatest version validated and tested\n\n# Use Case Description\n\nOne of our clients generated the VRF migration report in an exhausting time, in terms of the client, one week to validate each piece of equipment, ciberc-ca generates a comparative cross-validation report saving a lot of time and avoiding human errors.\n\n# Installation\n\n```\nUbuntu 20.04 or o any Distribution of Linux with support to Python3\n```\n\n# Steps to install in Ubuntu workstation (automation station)\n\n```\nprepare environment:\n  sudo apt-get install python3\n  sudo apt-get install git\n  sudo apt-get install python3-pip\n  python3 -m pip install virtualenv\n\n  mkdir code & cd code\n  python3 -m venv .venv\n  source .venv/bin/activate\n  python3 -m pip install cibercca\n\n```\n\n\n# Configuration\n\nThe first step is to create the inventory files, in these will go the record of the devices assigned to evaluate\n\n# Examples\n\n## Commands:\n\n```\nCommands:\n  alive       Alive for all device filter with groups\n  interfaces  Device interface information\n  inventory   Create files for inventory system\n  ping        report por vrf and ping results for inventory devices\n  ping-merge  Command to merge the source vrf listing files and...\n```\n\n### Alive command:\n\n```\nDescription: ping report of all inventory devices\n\nOptions:\n  --path TEXT\n  --group TEXT\n  --workers INTEGER\n  --output TEXT\n\nExample:\n    $ ciberc-ca alive --path=inventory/ --group=guatemala --workers=4 --output=json > alive-report.json\n```\n\n### Inventory files command:\n\n```\nDescription: create the necessary files to create the cyberc-ca system inventory\n\nOptions:\n  --create / --no-create  create files from inventory examples  [default: no-create]\n\nExample:\n    $ ciberc-ca inventory --create\n```\n\n### Interfaces command:\n\n```\nDescription: report interfaces of cisco ios devices currently, generates report in json as a summary in excel\n    - BVI\n    - Vlans\n    - trunk interfaces\n    - bridge-domain\n    - mac-address-table dynamic\n\nOptions:\n  --path PATH        The path to inventory  [required]\n  --group TEXT       The groups to filter inventory [required]\n  --workers INTEGER  The parallel execution  [default: 2]\n  --output TEXT      The type to print report  [default: json]\n  --mechanism TEXT   The excel mechanism to print report\n  --name TEXT        The name of excel report\n\nExample:\n    $ ciberc-ca interfaces --path=core/inventory/ --output=json > interfaces.json\n    $ ciberc-ca interfaces --path=core/inventory/ --output=excel --mechanism=row --name=interfaces > interfaces.json\n```\n\n\n### Ping command:\n\n```\nDescription: report por vrf and ping results for inventory devices\n\nOptions:\n  --path PATH        The path to inventory  [required]\n  --group TEXT       The groups to filter inventory  [required]\n  --workers INTEGER  The parallel execution  [default: 2]\n  --output TEXT      The type to print report  [default: json]\n  --name TEXT        The name of the excel file\n  --process TEXT     what type of process for the vrf report [src, dst] [required]\n  --help             Show this message and exit.\n\nExample:\n    $ ciberc-ca ping --path=core/inventory/ --group=src,guatemala,escuintla --output=json --name=ReportPingSource --process=src\n    $ ciberc-ca ping --path=core/inventory/ --group=dst,guatemala,escuintla --output=json --name=ReportPingDestinations --process=dst\n```\n\n### Ping-Merge command:\n\n```\nDescription: Command to merge the source vrf listing files and destination with validated report\n\nOptions:\n  --file-src TEXT  Vrf origin listing file  [required]\n  --file-dst TEXT  Target vrf listing file  [required]\n  --output TEXT    The type to print report  [required]\n  --name TEXT      The name of the excel file\n  --help           Show this message and exit.\n\nExample:\n    $ ciberc-ca ping-merge --file-src=file_vrfs_source.json --file-dst=file_vrf_destinations.json --output=excel --name=ReporteMigrations\n\n```\n\n# Structure\n\n```\ninventory/\n├── defaults.yaml\n├── groups.yaml\n└── hosts.yaml\n\n\nInventory is based on nornir structure\n\n  defaults.yaml: Contains all the default variables for the devices.\n\n  groups.yaml: Although based on nornir groups, two mandatory groups are needed for configuration, src, dst for the cross-validation ping-merge command.\n\n  hosts.yaml: where all IOS devices are registered for interface reporting, source IOS and destination XR for VRF's migration\n```\n\n\n# Usage\n\npara implementar el servicio una vez que haya definido los equipos en el archivo de hosts (aquí se define el usuario y la contraseña que se aplicará por tipo de dispositivo), los nombres de los dispositivos de red correctamente (en el archivo etc/hosts) y los dispositivos tienen la configuración de SSH, entonces colocaría los comandos de ejemplo para activar el agente ssh y xml en XR.\n\n# configuration example in XR device\n```\n# default.yaml\n---\ndata:\n  domain: local.local\n\n\n# groups.yaml\n---\n# {} => ejemplo\nguatemala: {}\n\n# for the ping report, it contains all the source computers\nsrc: {}\n\n# for the ping report, it contains all the destination computers\ndst: {}\n\n\n# hosts.yaml\n---\nR1:\n  hostname: localhost\n  port: 22\n  username: user\n  password: secret\n  platform: ios\n  groups:\n    - guatemala\n    - src # used to separate the source computers from the migration\n\nR2:\n  hostname: localhost\n  port: 22\n  username: user\n  password: secret\n  platform: iosxr\n  data:\n    source: R1 # to which device does the migration belong, virtual link to compare reports\n  groups:\n    - guatemala\n    - dst # used to separate the migration destination computers\n\n\n```\n\n\n# How to test the software\n\nyou can check the configuration in the devices in the generated report\n\n# Getting help\n\nIf you have questions, concerns, bug reports, etc., please create an issue against this repository, or send me an email to: Dev.auto@ciberc.com\n\n# Link Video Example\nhttps://www.youtube.com/watch?v=d_Vwdx62hG8\n",
    'author': 'Rafael Garcia Sagastume',
    'author_email': 'rafael.garcia@ciberc.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
