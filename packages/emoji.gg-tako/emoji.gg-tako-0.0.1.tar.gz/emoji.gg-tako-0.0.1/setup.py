from distutils.core import setup
setup(
  name = 'emoji.gg-tako',
  packages = ['emoji-gg'],
  version = '0.0.1',
  license= 'MIT',
  description = 'Unofficial API Wrapper for emoji.gg',
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
