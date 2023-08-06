# -*- coding: utf-8 -*-


import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('wskbb/wskbb.py').read(),
    re.M
    ).group(1)


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name = "wskbb",
    packages = ["wskbb"],
    entry_points = {
        "console_scripts": ['wskbb = wskbb.wskbb:main']
    },
    scripts=['bin/wskbb'],
    version = version,
    description = "Command line untuk mengubah image menjadi ala karya Papin dan Agung Botol",
    long_description = readme(),
    author = "Lantip",
    author_email = "lantip@gmail.com",
    url = "https://lantip.xyz",
    install_requires=[
        'opencv-python==4.6.0.66',
        'scikit-image==0.19.3',
        'matplotlib==3.5.2',
        'scikit-learn==1.1.1',
    ]
    )
