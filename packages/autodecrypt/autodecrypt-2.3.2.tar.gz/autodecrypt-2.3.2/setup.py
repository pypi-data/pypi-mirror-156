# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autodecrypt']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0',
 'pyimg4>=0.6.2,<0.7.0',
 'pyquery>=1.4.1,<2.0.0',
 'pyusb>=1.0.2,<2.0.0',
 'remotezip>=0.9.2,<0.10.0',
 'rich>=12.4.4,<13.0.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['autodecrypt = autodecrypt.main:app']}

setup_kwargs = {
    'name': 'autodecrypt',
    'version': '2.3.2',
    'description': 'Tool to decrypt iOS firmware images',
    'long_description': '# autodecrypt\n[![PyPI version](https://badge.fury.io/py/autodecrypt.svg)](https://badge.fury.io/py/autodecrypt)\n\nSimple tool to decrypt iOS firmware images.\n\nGoing to the iPhone wiki and copying and pasting firmware keys to your terminal is boring.\n\nautodecrypt will grab keys for you and decrypt the firmware image you want.\n\n## Usage\n```\nUsage: autodecrypt [OPTIONS]\n\nOptions:\n  -f, --filename TEXT             File  [required]\n  -d, --device TEXT               Device  [required]\n  -i, --ios_version TEXT          iOS version\n  -b, --build TEXT                Build ID of iOS version\n  -k, --ivkey TEXT                IV and key to decrypt file\n  -l, --local                     Use path to local file\n  -D, --download                  Download file\n  -B, --beta                      Specify that it is a beta firmware\n  -P, --pongo                     Use PongoOS over USB for decryption\n  --install-completion [bash|zsh|fish|powershell|pwsh]\n                                  Install completion for the specified shell.\n  --show-completion [bash|zsh|fish|powershell|pwsh]\n                                  Show completion for the specified shell, to\n                                  copy it or customize the installation.\n  --help                          Show this message and exit.\n```\n\n## Dependencies\n- [img4](https://github.com/xerub/img4lib)\n\nTo run autodecrypt, use poetry with a virtualenv:\n- `virtualenv -p python3 env`\n- `pip3 install poetry`\n- `poetry install`\n\n\n## Installation\n`pip3 install autodecrypt`\n\n\n## Examples\n\n#### Download and decrypt iBSS using keys from theiphonewiki\n```\n» autodecrypt -f iBSS.iphone6.RELEASE.im4p -i 10.3.3 -d iPhone6,2\n[i] downloading iBSS.iphone6.RELEASE.im4p\n[i] image : ibss\n[i] grabbing keys for iPhone6,2/14G60\n[x] iv  : f2aa35f6e27c409fd57e9b711f416cfe\n[x] key : 599d9b18bc51d93f2385fa4e83539a2eec955fce5f4ae960b252583fcbebfe75\n[i] decrypting iBSS.iphone6.RELEASE.im4p to iBSS.iphone6.RELEASE.bin...\n[x] done\n```\n\n#### Download and decrypt SEP firmware by specifying keys\n```\n» autodecrypt -f sep-firmware.n841.RELEASE.im4p -b 17C5053a -d iPhone11,8 -k 9f974f1788e615700fec73006cc2e6b533b0c6c2b8cf653bdbd347bc1897bdd66b11815f036e94c951250c4dda916c00\n[i] downloading sep-firmware.n841.RELEASE.im4p\n[x] iv  : 9f974f1788e615700fec73006cc2e6b5\n[x] key : 33b0c6c2b8cf653bdbd347bc1897bdd66b11815f036e94c951250c4dda916c00\n[i] decrypting sep-firmware.n841.RELEASE.im4p to sep-firmware.n841.RELEASE.bin...\n[x] done\n```\n\n#### Use [foreman](https://github.com/GuardianFirewall/foreman) instance to grab firmware keys\n```\n» export FOREMAN_HOST="https://foreman-public.sudosecuritygroup.com"\n» autodecrypt -f LLB.n112.RELEASE.im4p -i 13.2.3 -d iPod9,1\n[i] downloading LLB.n112.RELEASE.im4p\n[i] image : llb\n[i] grabbing keys for iPod9,1/17B111\n[i] grabbing keys from https://foreman-public.sudosecuritygroup.com\n[x] iv  : 85784a219eb29bcb1cc862de00a590e7\n[x] key : f539c51a7f3403d90c9bdc62490f6b5dab4318f4633269ce3fbbe855b33a4bc7\n[i] decrypting LLB.n112.RELEASE.im4p to LLB.n112.RELEASE.bin...\n[x] done\n```\n\n#### Decrypt keys with PongoOS\n> I you wanna use this on Linux, you may have some USB permissions. I recommend copying the file `66-pongos.rules` available on this repository to `/etc/udev/rules.d/`.\n\n```\n» autodecrypt -f iBoot.n71.RELEASE.im4p -d iPhone8,1 -i 14.1 -p\n[i] downloading iBoot.n71.RELEASE.im4p\n[i] grabbing keys from PongoOS device\n[i] kbag : 03C9E01CA99FE6475566C791777169C0625B04B7BD4E593DE0F61ABF4E8DB1A987D9D6155C5A1F41D9113694658AC61C\n[x] iv  : 245a9b52e53a704fe73d7b58734b00ae\n[x] key : d3aa3c8cc20fa9d61e466f46aee374a92a125abb5b3f57264025c8c72127e321\n[i] decrypting iBoot.n71.RELEASE.im4p to iBoot.n71.RELEASE.bin...\n[x] done\n```\n\n#### Log\n\nFor debugging purposes you can check `autodecrypt.log` :\n```\n11/02/2019 21:39:41 Launching "[\'autodecrypt/autodecrypt.py\', \'-d\', \'iPhone9,3\', \'-f\', \'iBoot.d10.RELEASE.im4p\', \'-i\', \'12.3.1\']"\n11/02/2019 21:39:41 requesting IPSW\'s API for iPhone9,3\n11/02/2019 21:39:41 done, now looking for version or build\n11/02/2019 21:39:41 grabbing firmware codename for 16F203\n11/02/2019 21:39:42 codename : PeaceF\n11/02/2019 21:39:42 grabbing IPSW file URL for iPhone9,3/12.3.1\n11/02/2019 21:39:42 downloading iBoot...\n11/02/2019 21:39:43 img4 -i iBoot.d10.RELEASE.im4p iBoot.d10.RELEASE.bin 978fd4680cd4b624b0dfea22a417f51f0ee2b871defed42277fe18885053b1eb5c7ffe82f38ab8cf7772c69a0db5d386\n```\n\n\n### Credits\n- checkra1n team for AES patches, kbag.m and [PongoOS](https://github.com/checkra1n/pongoos)\n- tihmstar for wiki parsing ([my method](https://github.com/matteyeux/ios-tools/blob/master/scrapkeys.py) was pretty bad)\n- m1stadev for [PyIMG4](https://github.com/m1stadev/PyIMG4)\n\n',
    'author': 'matteyeux',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/matteyeux/autodecrypt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
