from setuptools import setup, find_packages

setup(
    name='insighta-cli',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'rich',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'insighta=cli_tool.main:cli', # This enables 'insighta' globally [cite: 218]
        ],
    },
)