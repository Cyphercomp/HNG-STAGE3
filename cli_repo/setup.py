# setup.py (Root of cli-repo)
from setuptools import setup, find_packages

setup(
    name='insighta-cli',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'click',
        'rich',
    ],
    entry_points={
        'console_scripts': [
            'insighta=cli.commands:cli', # Points to the 'cli' group in commands.py
        ],
    },
)