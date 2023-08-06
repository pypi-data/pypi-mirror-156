# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dumpscan',
 'dumpscan.common',
 'dumpscan.common.scanners',
 'dumpscan.kernel',
 'dumpscan.kernel.plugins',
 'dumpscan.minidump',
 'dumpscan.minidump.structs']

package_data = \
{'': ['*']}

install_requires = \
['arrow>=1.2.2,<2.0.0',
 'capstone>=5.0.0rc2,<6.0.0',
 'cffi>=1.15.0,<2.0.0',
 'construct>=2.10.68,<3.0.0',
 'cryptography>=37.0.2,<38.0.0',
 'jsonschema>=4.5.1,<5.0.0',
 'pefile>=2022.5.30,<2023.0.0',
 'pycryptodome>=3.14.1,<4.0.0',
 'rich-click[typer]>=1.4,<2.0',
 'rich>=12.3.0,<13.0.0',
 'typer>=0.4.1,<0.5.0',
 'yara-python>=3.8.0']

entry_points = \
{'console_scripts': ['dumpscan = dumpscan.main:app']}

setup_kwargs = {
    'name': 'dumpscan',
    'version': '0.1.0',
    'description': 'Scanning memory dumps for secrets using volatility and yara',
    'long_description': '\n<p align="center">\n  <img width="500" height="500" src="https://raw.githubusercontent.com/daddycocoaman/dumpscan/main/docs/dumpscan.png">\n</p>\n\n**Dumpscan** is a command-line tool designed to extract and dump secrets from kernel and Windows Minidump formats. Kernel-dump parsing is provided by [volatility3](https://github.com/volatilityfoundation/volatility3).\n\n## Features\n\n- x509 Public and Private key (PKCS #8/PKCS #1) parsing\n- [SymCrypt](https://github.com/microsoft/SymCrypt) parsing\n  - Supported structures\n    - **SYMCRYPT_RSAKEY** - Determines if the key structure also has a private key\n  - Matching to public certificates found in the same process\n  - More SymCrypt structures to come\n- Environment variables\n- Command line arguments\n\n**Note**: Testing has only been performed on Windows 10 and 11 64-bit hosts and processes. Feel free to file an issue for additional versions. Linux testing TBD.\n\n## Installation\n\nAs a command-line tool, installation is recommended using [pipx](https://github.com/pypa/pipx). This allows for easy updates and well and ensuring it is installed in its own virtual environment.\n\n```\npipx install dumpscan\npipx inject dumpscan git+https://github.com/volatilityfoundation/volatility3#39e812a\n```\n\n## Usage\n\n```\n Usage: dumpscan [OPTIONS] COMMAND [ARGS]...\n\n Scan memory dumps for secrets and keys\n\n╭─ Options ────────────────────────────────────────────────────────────────────────────────────────╮\n│                                                                                                  │\n│  --help         Show this message and exit.                                                      │\n│                                                                                                  │\n╰──────────────────────────────────────────────────────────────────────────────────────────────────╯\n╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────╮\n│                                                                                                  │\n│  kernel     Scan kernel dump using volatility                                                    │\n│  minidump   Scan a user-mode minidump                                                            │\n│                                                                                                  │\n╰──────────────────────────────────────────────────────────────────────────────────────────────────╯\n```\n\nIn the case for subcommands that extract certificates, you can provide `--output/-o <dir>` to output any discovered certificates to disk.  \n\n### Kernel Mode\n\nAs mentioned, kernel analysis is performed by Volatility3. `cmdline`, `envar`, and `pslist` are direct calls to the Volatility3 plugins, while `symcrypt` and `x509` are custom plugins.\n\n```\n Usage: dumpscan kernel [OPTIONS] COMMAND [ARGS]...\n\n Scan kernel dump using volatility\n\n╭─ Options ────────────────────────────────────────────────────────────────────────────────────────╮\n│                                                                                                  │\n│  --help         Show this message and exit.                                                      │\n│                                                                                                  │\n╰──────────────────────────────────────────────────────────────────────────────────────────────────╯\n╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────╮\n│                                                                                                  │\n│  cmdline    List command line for processes (Only for Windows)                                   │\n│  envar      List process environment variables (Only for Windows)                                │\n│  pslist     List all the processes and their command line arguments                              │\n│  symcrypt   Scan a kernel-mode dump for symcrypt objects                                         │\n│  x509       Scan a kernel-mode dump for x509 certificates                                        │\n│                                                                                                  │\n╰──────────────────────────────────────────────────────────────────────────────────────────────────╯\n```\n\n### Minidump Mode\n\nSupports Windows Minidump format.\n\n**Note**: This has only been tested on 64-bit processes on Windows 10+. 32-bit processes requires additional work but isn\'t a priority.\n\n\n```\n Usage: dumpscan minidump [OPTIONS] COMMAND [ARGS]...\n\n Scan a user-mode minidump\n\n╭─ Options ────────────────────────────────────────────────────────────────────────────────────────╮\n│                                                                                                  │\n│  --help         Show this message and exit.                                                      │\n│                                                                                                  │\n╰──────────────────────────────────────────────────────────────────────────────────────────────────╯\n╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────╮\n│                                                                                                  │\n│  cmdline    Dump the command line string                                                         │\n│  envar      Dump the environment variables in a minidump                                         │\n│  symcrypt   Scan a minidump for symcrypt objects                                                 │\n│  x509       Scan a minidump for x509 objects                                                     │\n│                                                                                                  │\n╰──────────────────────────────────────────────────────────────────────────────────────────────────╯\n```\n\n## Built With\n- [volatility3](https://github.com/volatilityfoundation/volatility3)\n- [construct](https://github.com/construct/construct)\n- [yara-python](https://github.com/VirusTotal/yara-python)\n- [typer](https://github.com/tiangolo/typer)\n- [rich](https://github.com/Textualize/rich)\n- [rich_click](https://github.com/ewels/rich-click)\n  \n## Acknowledgements\n- Thanks to [F-Secure](https://github.com/FSecureLABS) and the [physmem2profit](https://github.com/FSecureLABS/physmem2profit) project for providing the idea to use `construct` for parsing minidumps.\n- Thanks to [Skelsec](https://github.com/skelsec) and his [minidump](https://github.com/skelsec/minidump) project which helped me figure out to parse minidumps.\n\n\n## To-Do\n\n- Verify use against 32-bit minidumps\n- Create a coredump parser for Linux process dumps\n- Verify volatility plugins work against Linux kernel dumps\n- Add an HTML report that shows all plugins\n- Code refactoring to make more extensible\n- MORE SECRETS',
    'author': 'Leron Gray',
    'author_email': 'daddycocoaman@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
