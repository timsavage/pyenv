#!/usr/bin/env python
import bs4
import requests

from collections import namedtuple
from io import StringIO

RELEASES_URL = "http://downloads.activestate.com/ActivePython/releases/"
HEADER = 'case "$(activepython_architecture 2>/dev/null || true)" in'
FOOTER = """
*)
  { echo
    colorize 1 "ERROR"
    echo ": The binary distribution of Active Python is not available for $(activepython_architecture 2>/dev/null || true)."
    echo
  } >&2
  exit 1
  ;;
esac
""".strip()

Package = namedtuple("Package", ('id', 'url', 'version', 'hash'))

# Get available versions
print("Getting available releases...")
response = requests.get(RELEASES_URL)
doc = bs4.BeautifulSoup(response.content, 'html.parser')
pre = doc.find('pre')
releases = []
for link in pre.find_all('a'):
    href = link.get('href')
    if href[0] not in '?/.':
        releases.append(href)

releases = releases[:1]
release_packages = {}

# Iterate and read in SHA256SUM files
for release in releases:
    print("Getting packages for release:", release)
    release_url = RELEASES_URL + release
    sha_url = release_url + 'SHA256SUM'
    release_packages[release] = []
    
    response = requests.get(sha_url)
    sha_file = StringIO(response.content.decode())
    for line in sha_file:
        h, f = line.strip().split()
        release_packages[release].append("{}{}#{}".format(release_url, f, h))

# Generate entries
for release, packages in release_packages.items():
    print("Release: ", release, "\n", '=' * 20, '\n', sep='')

    print(HEADER)
    for package in packages:    
        if 'linux-x86_64' in package:
            print('"linux-x86_64" )\n  install_package "{}" "{}" "activepython" verify_{}\n  ;;'.format("ActivePython...", package, "pyXX"))
        elif 'linux-x86' in package:
            print('"linux-x86" )\n  install_package "{}" "{}" "activepython" verify_{}'.format("ActivePython...", package, "pyXX"))
        elif 'win64' in package:
            print('# "win64" )\n#   {}\n#   ;;'.format(package))
        elif 'macosx10.9' in package:
            print('# "macosx10.9" )\n#   {}\n#   ;;'.format(package))
    print(FOOTER)

