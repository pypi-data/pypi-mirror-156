# -*- coding: utf-8 -*-
try:
    from setuptools import find_packages, setup
except ImportError:
    from ez_setup import use_setuptools

    use_setuptools()
    from setuptools import find_packages, setup

setup(
    name="demo_sdk",
    install_requires=["fabric3"],
    author="kasiramkompella",
    author_email="kasiramkompella@gmail.com",
    zip_safe=True,
    include_package_data=True,
    packages=find_packages(exclude=["ez_setup"]),
)
