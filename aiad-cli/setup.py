# This file was automatically generated by Shore. Do not edit manually.
# For more information on Shore see https://pypi.org/project/nr.shore/

import io
import re
import setuptools
import sys

with io.open('src/aiad_cli/__init__.py', encoding='utf8') as fp:
  version = re.search(r"__version__\s*=\s*'(.*)'", fp.read()).group(1)

with io.open('README.md', encoding='utf8') as fp:
  long_description = fp.read()

requirements = ['beautifulsoup4 >=4.9.1,<5.0.0', 'click >=7.1.2,<8.0.0', 'nr.databind.core >=0.0.14,<0.1.0', 'nr.databind.json >=0.0.9,<0.1.0', 'nr.interface >=0.0.2,<0.1.0', 'nr.proxy >=0.0.2,<0.1.0', 'requests >=2.23.0,<3.0.0', 'termcolor >=1.1.0,<2.0.0']

setuptools.setup(
  name = 'aiad-cli',
  version = version,
  author = 'Niklas Rosenstein',
  author_email = 'rosensteinniklas@gmail.com',
  description = 'CLI to manage the An Image a Day Wallpaper database.',
  long_description = long_description,
  long_description_content_type = 'text/markdown',
  url = None,
  license = 'MIT',
  packages = setuptools.find_packages('src', ['test', 'test.*', 'docs', 'docs.*']),
  package_dir = {'': 'src'},
  include_package_data = True,
  install_requires = requirements,
  extras_require = {},
  tests_require = [],
  python_requires = None, # TODO: '>=3.4,<4.0.0',
  data_files = [],
  entry_points = {
    'aiad_cli.resolvers': [
      'pexels = aiad_cli.resolvers.pexels:PexelsWallpaperSpecResolver',
      'unsplash = aiad_cli.resolvers.unsplash:UnsplashWallpaperSpecResolver',
      'wallpapershome = aiad_cli.resolvers.wallpapershome:WallpapersHomeSpecResolver',
    ],
    'console_scripts': [
      'aiad-cli = aiad_cli.__main__:cli',
    ]
  },
  cmdclass = {},
  keywords = [],
  classifiers = [],
)
