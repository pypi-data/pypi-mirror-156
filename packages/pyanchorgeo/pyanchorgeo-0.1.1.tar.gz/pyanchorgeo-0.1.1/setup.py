from setuptools import setup, find_packages

setup(
    name='pyanchorgeo',
    version='0.1.1',
    packages=find_packages(include=['pyanchor', 'pyanchor.*']),
    install_requires=[
        'numpy',
    ]
)