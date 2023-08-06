from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.2'
DESCRIPTION = 'SDK sanic application'

# Setting up
setup(
    name="sdk_sw_sanic",
    version=VERSION,
    author="swalih",
    author_email="<swalihchungath@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['opencv-python', 'sanic', 'cryptography','numpy','pytest'],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'palm'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)