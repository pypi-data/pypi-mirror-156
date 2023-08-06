import os

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='uiipythonapi',
    version='1.0.0',
    url='https://github.com/virtomize/uii-python-api',
    author='Virtomize GmbH',
    author_email='api@virtomize.com',
    description="A client implemenation for Virtomize Unattended Install Images API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='BSD 2-clause',
    packages=['uiipythonapi'],
    package_dir={'uiipythonapi': 'src/uiipythonapi'},
    install_requires=[
        'requests'
    ],

    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.8',
    ],
)
