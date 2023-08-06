# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['iTunesContactsExport',
 'iTunesContactsExport.iTunesDatabase',
 'iTunesContactsExport.vCard']

package_data = \
{'': ['*']}

install_requires = \
['vobject>=0.9.6.1,<0.10.0.0']

entry_points = \
{'console_scripts': ['iTunesContactsExport = '
                     'iTunesContactsExport.__main__:main']}

setup_kwargs = {
    'name': 'itunescontactsexport',
    'version': '0.1.0',
    'description': 'This small program will export your contact from an itunes backup.',
    'long_description': '# A sad IPHone story ...\nI wrote this python script after my iPhone had a unrepairable hardware failure and a corrupt iTunes backup that could not be restored on my new iPhone!\nI was losing pictures but not that much as I regularly extracts them, but it was a totally different story for the contacts, as iTunes offers no way to extract them and I refuse to send my data to iCloud.\nI search for a way to recover my contacts and I found not only many applications that all promise that they will repair and/ore recover you data, but also simple script that extract them from the database of the address book. You just need a backup from iTunes. \nSo I decided to write my own version that extracts all the fields I need in a vCard 3.0 format. I do not intend to cover all the cases but i think it is already quite complete, and I hope it will help others. \nI took this opportunity to write it in python, language that I barely know, so i ask for mercy to the experts in Python because I probably do not follow theirs best practice :)\n\n# Install\n## prerequisits\n- python >=3.9 [prerequisits]([https://www.python.org/downloads/])\n- pip\n- pipx (optional)\n## Intall \n```\n    pip install itunescontactsexport\n```\nor\n```\n    pip install pipx\n    pipx install itunescontactsexport\n```\n \n# Usage\n There 2 modes to use this script:\n - iTunes mode: You need to have access to the directory of a iTunes backup of your phone. The script will figure out where are the databases of the address book and export the contacts\n - db: You need to provide the path to the address book you want to export and optionally the path to the iamges database of the address book\n\nThe image quality refer to the available thumbnail in our thumbnail database:\n- originale: it use the originale image with no transformation\n- best: use the thumbnail with the highest resolution\n- lowest: use the thumbnail with the lowest resolution.\n## Backup from iTunes\n ```usage: iTunesContactsExport itunes [-h] [-bday] [-q {best,lowest,orig}] [-o outputFile] backupDir\n\npositional arguments:\n  backupDir             Path to the directory of the Itunebackup\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -bday                 Use BDAY instead of ANNIVERSARY (not iphone friendly\n  -q {best,lowest,orig}\n                        Image quality: best, lowest, originale\n  -o outputFile         Path to export file\n```\n## Backup from db\n ```usage: iTunesContactsExport db [-h] [-bday] [-q {best,lowest,orig}] [-i imagesDBPath] [-o outputFile] addressBookDBPath\n\npositional arguments:\n  addressBookDBPath     Path to the addressbook database\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -bday                 Use BDAY instead of ANNIVERSARY (not iphone friendly\n  -q {best,lowest,orig}\n                        Image quality: best, lowest, originale\n  -i imagesDBPath       Path to the images database\n  -o outputFile         Path to export file\n```\n# Limitations\nThe attributs exported to the vcard are:\n- uid of the contact\n- last modification of the vcard\n- Name (Given, middle, Familly)\n- Nickname\n- job title\n- Phones numbers\n- Addresses\n- emails\n- Birthday\n- relatives\n- images\n- Notes\n- urls\n',
    'author': 'Tinigriffy',
    'author_email': 'beistin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Tinigriffy/iTunesContactsExport',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
