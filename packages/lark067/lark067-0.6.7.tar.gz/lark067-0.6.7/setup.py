from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = "lark067",
    version = '0.6.7',
    packages = ['lark', 'lark.parsers', 'lark.tools', 'lark.grammars'],

    requires = [],
    install_requires = [],

    package_data = { '': ['*.md', '*.lark'] },

    test_suite = 'tests.__main__',

    author = "Erez Shinan",
    description = "a modern parsing library",
    license = "MIT",
    keywords = "Earley LALR parser parsing ast",
    url = "https://github.com/skieffer/lark",
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
    ],

)

