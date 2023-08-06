# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mirrorlib']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mirrorlib',
    'version': '0.1.0',
    'description': 'A generic specification for mirroring data',
    'long_description': '# mirrorlib\n\nmirrorlib is a flat, generic specification for tracking urls and files together. The strength of mirrorlib is its simplicity and ability to track any type of data. It is designed to make data verification and integrity easy and provide all the data upfront to manage your mirror. mirrorlib is not designed to be the *fastest* mirror specification, but to be as portable and simple as possible. This allows many developers to quickly develop on top of the code and have the flexibility to use the data as they please.\n\nmirrorlib was inspired by [RedoxOS](https://web.archive.org/web/20220521191003/https://doc.redox-os.org/book/ch04-10-everything-is-a-url.html) and their philosophy of "everything is a URL". In mirrorlib everything is a URI that is tracked together in one place.\n\nmirrorlib is not specific to any type of database and can be implemented using any language, you could even implement it as a JSON file if you wanted to. The reference implementation is currently implemented using python and sqlite. It\'s not required, but all data is usually stored in a single table called \'mirror\'. A mirror contains only URIs and their associated metadata as text.\n\n## Getting Started\n\n```\npip install mirrorlib\n```\n\n## Documentation\n\n\n\n## Golden rules\n\n- Everything is a URI\n- Use text as much as possible\n- Keep data simple\n\n## Contributing\n\n## TODO\n\nThe specification and reference implementation is still being developed and any suggestions and issues are welcome.\n\nThe longterm goal is to implement the reference specification in Rust and use Python bindings instead. For the time being\n\n## History\n\nmirrorlib was originally created to be used in another archiving project, youmirror. Youmirror is a tool developed in early 2022 for downloading and archiving media, originally Youtube videos. However, I\'m always looking for ways that components of larger projects can be broken down into modules that may be helpful more broadly. I am hoping that mirrorlib will be used to archive all kinds of data and inspire even better projects in the future!',
    'author': 'wkrettek',
    'author_email': '50168688+wkrettek@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
