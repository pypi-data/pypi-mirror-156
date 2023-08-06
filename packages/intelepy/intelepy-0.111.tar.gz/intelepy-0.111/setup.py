from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="intelepy",
    version="0.111",
    author="Michael Ralston",
    author_email="michaelaaralston2@gmail.com",
    description="Intelepeer API Wrapper",
    license="MIT",
    url="https://github.com/MichaelRalston98/intelepy",
    keywords=["Intelepeer", "ITSP"],
    packages=["intelepy"],
    install_requires=[
        'json',
        'requests',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)