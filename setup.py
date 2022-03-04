from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='sus',
    version='0.1a',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    entry_points={
    'console_scripts':
        ['sus = sus:main']
    }
)
