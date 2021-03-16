from setuptools import setup

VERSION = "0.1.0"

setup(
    name="hass-uniocloud",
    version=VERSION,
    license="GPL v3",
    author="UNIO Smart Home",
    author_email="developers@freshminds.com.br",
    url="https://www.uniosmarthome.com",
    download_url="https://github.com/uniosmarthome/hass-uniocloud/tarball/{}".format(VERSION),
    description=("Home Assistant cloud integration by UNIO Smart Home"),
    long_description=(""),
    classifiers=[
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.8",
    ],
    keywords=["homeassistant", "cloud", "unio"],
    zip_safe=False,
    platforms="any",
    packages=["hass_uniocloud"],
    install_requires=[
        "pycognito==0.1.4",
        "snitun==0.20",
        "acme==1.9.0",
        "cryptography>=2.8,<4.0",
        "attrs>=19.3,<20.4",
        "pytz>=2019.3",
        "aiohttp>=3.6.1",
        "atomicwrites==1.4.0",
    ],
)
