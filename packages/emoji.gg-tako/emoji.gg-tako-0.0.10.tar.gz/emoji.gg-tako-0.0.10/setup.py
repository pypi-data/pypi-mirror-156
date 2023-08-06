from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

def read_requirements():
    with open('requirements.txt', 'r') as req:
        content = req.read()
        requirements = content.split('\n')

    return requirements


setup(
    name='emoji.gg-tako',
    version='0.0.10',
    author='Pukima',
    author_email='pukima@pukima.site',
    description = '(Unofficial) API Wrapper for emoji.gg',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/kayano-bot/EmojiGG-Wrapper',
    project_urls={
        "Source Code": "https://github.com/kayano-bot/EmojiGG-Wrapper",
        "Discord": "https://discord.gg/dfmXNTmzyp",
        "Issue tracker": "https://github.com/kayano-bot/EmojiGG-Wrapper/issues"
    },
    packages=["emoji_gg"],
    include_package_data=True,
    install_requires=read_requirements(),
    keywords=["python", "emojigg", "apiwrapper"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ]
)