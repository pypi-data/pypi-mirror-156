import os
from distutils.core import setup

def __read__(file_name: str):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()

setup(
  name = 'emoji.gg-tako',
  packages = ['emoji-gg'],
  version = '0.0.2',
  license= 'MIT',
  description = 'Unofficial API Wrapper for emoji.gg',
  long_description_content_type="text/markdown",
  long_description=__read__("README.md"),
  author = 'Pukima',
  author_email = 'pukima@pukima.site',
  url = 'https://github.com/kayano-bot/EmojiGG-Wrapper',
  keywords = ['apiwrapper', 'emojigg'],
  install_requires=[
    'aiohttp',
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
