# -*- coding: utf-8 -*-
# @Time : 2022/5/31 0:45
# @Author : Zhongyi Hua
# @FileName: setup.py.py
# @Usage: 
# @Note:
# @E-mail: njbxhzy@hotmail.com

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TriGeneI",
    version="0.1",
    author="Zhongyi Hua",
    author_email="njbxhzy@hotmail.com",
    description="TGMI network inference using Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hua-CM/TGMI",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    install_requires=["pathos", "pandas", "SciPy"],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3",
)
