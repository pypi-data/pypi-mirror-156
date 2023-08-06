from setuptools import setup, find_packages
import os

_here = os.path.abspath(os.path.dirname(__file__))

# Store the README.md file
with open(os.path.join(_here, "README.md"), encoding="utf-8") as f:
    longDescription = f.read()

setup(
    name='pyanchorgeo',
    version='0.1.2',
    packages=find_packages(include=['pyanchor', 'pyanchor.*']),
    install_requires=[
        'numpy',
    ],
    license="MIT",  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description="Ground anchor capacity using the Bustamante and Doix (1985) empirical method",  # Give a short description about your library
    long_description=longDescription,
    long_description_content_type="text/markdown",
    author_email="info@civils.ai",  # Type in your E-Mail
    url="https://github.com/tunnelsai-public/PyAnchor",  # Provide either the link to your github or to your website
)